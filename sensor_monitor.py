import time
from typing import Callable, Dict, Optional


class ThresholdState:
	def __init__(
		self,
		low: Optional[float],
		high: Optional[float],
		hysteresis: float,
		*,
		smoothing_alpha: float,
		min_duration_s: float,
		cooldown_s: float,
	):
		self.low = low
		self.high = high
		self.hysteresis = hysteresis
		self.alpha = smoothing_alpha
		self.min_duration_s = min_duration_s
		self.cooldown_s = cooldown_s

		self._smoothed: Optional[float] = None
		self._is_low: bool = False
		self._is_high: bool = False
		self._cross_start_ts: Optional[float] = None
		self._last_event_ts: float = 0.0

	def _smooth(self, value: float) -> float:
		if self._smoothed is None:
			self._smoothed = value
		else:
			self._smoothed = self.alpha * value + (1.0 - self.alpha) * self._smoothed
		return self._smoothed

	def update(self, value: float, ts: Optional[float] = None) -> Optional[str]:
		"""
		Returns one of: "enter_low", "exit_low", "enter_high", "exit_high", or None
		"""
		ts = ts if ts is not None else time.monotonic()
		v = self._smooth(value)

		# Low threshold logic with hysteresis
		if self.low is not None:
			low_enter = v <= self.low
			low_exit = v >= (self.low + self.hysteresis)
		else:
			low_enter = False
			low_exit = False

		# High threshold logic with hysteresis
		if self.high is not None:
			high_enter = v >= self.high
			high_exit = v <= (self.high - self.hysteresis)
		else:
			high_enter = False
			high_exit = False

		candidate_event: Optional[str] = None

		if not self._is_low and low_enter:
			candidate_event = "enter_low"
		elif self._is_low and low_exit:
			candidate_event = "exit_low"
		elif not self._is_high and high_enter:
			candidate_event = "enter_high"
		elif self._is_high and high_exit:
			candidate_event = "exit_high"

		if candidate_event is None:
			self._cross_start_ts = None
			return None

		if self._cross_start_ts is None:
			self._cross_start_ts = ts

		if (ts - self._cross_start_ts) < self.min_duration_s:
			return None

		if (ts - self._last_event_ts) < self.cooldown_s:
			return None

		# Commit state changes
		if candidate_event == "enter_low":
			self._is_low = True
		elif candidate_event == "exit_low":
			self._is_low = False
		elif candidate_event == "enter_high":
			self._is_high = True
		elif candidate_event == "exit_high":
			self._is_high = False

		self._last_event_ts = ts
		self._cross_start_ts = None
		return candidate_event


class MultiSensorMonitor:
	def __init__(
		self,
		thresholds: Dict[str, Dict[str, float]],
		*,
		smoothing_alpha: float = 0.25,
		min_duration_s: float = 0.5,
		cooldown_s: float = 2.0,
		on_event: Optional[Callable[[str, str, float], None]] = None,
	):
		"""
		thresholds example per sensor:
		{
			"soil_moisture": {"low": 35.0, "high": 80.0, "hysteresis": 2.0},
			"temperature_c": {"low": 18.0, "high": 30.0, "hysteresis": 0.5},
		}
		"""
		self.on_event = on_event
		self._states: Dict[str, ThresholdState] = {}
		for sensor_name, cfg in thresholds.items():
			low = cfg.get("low")
			high = cfg.get("high")
			hyst = cfg.get("hysteresis", 0.0)
			self._states[sensor_name] = ThresholdState(
				low, high, hyst,
				smoothing_alpha=smoothing_alpha,
				min_duration_s=min_duration_s,
				cooldown_s=cooldown_s,
			)

	def update(self, sensor_readings: Dict[str, float]) -> None:
		"""
		Feed one snapshot of readings: {sensor_name: value}
		"""
		for sensor_name, value in sensor_readings.items():
			state = self._states.get(sensor_name)
			if state is None:
				continue
			event = state.update(value)
			if event and self.on_event:
				self.on_event(sensor_name, event, value)

import time
from typing import Callable, Dict, Optional, Any


class ThresholdBandMonitor:
    """
    Monitors a single numeric signal for low/high threshold crossings with:
      - exponential smoothing
      - hysteresis (separate enter/exit thresholds)
      - dwell-time (min_duration_s) before firing
      - cooldown per event type to avoid spamming

    Events emitted:
      - enter_low / exit_low
      - enter_high / exit_high
    """

    def __init__(
        self,
        *,
        low_threshold: Optional[float] = None,
        high_threshold: Optional[float] = None,
        hysteresis: float = 0.0,
        smoothing_alpha: float = 0.2,
        min_duration_s: float = 0.5,
        cooldown_s: float = 2.0,
        on_event: Optional[Callable[[str, float, float], None]] = None,
    ) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.hysteresis = hysteresis
        self.alpha = smoothing_alpha
        self.min_duration_s = min_duration_s
        self.cooldown_s = cooldown_s
        self.on_event = on_event

        self._smoothed: Optional[float] = None
        self._state: str = "normal"  # normal | low | high
        self._cross_start_ts: Optional[float] = None
        self._last_event_ts: Dict[str, float] = {
            "enter_low": 0.0,
            "exit_low": 0.0,
            "enter_high": 0.0,
            "exit_high": 0.0,
        }

    def _smooth(self, value: float) -> float:
        if self._smoothed is None:
            self._smoothed = value
        else:
            self._smoothed = self.alpha * value + (1.0 - self.alpha) * self._smoothed
        return self._smoothed

    def _emit(self, event_type: str, v: float, ts: float) -> None:
        self._last_event_ts[event_type] = ts
        if self.on_event is not None:
            self.on_event(event_type, v, ts)

    def update(self, value: float, ts: Optional[float] = None) -> Optional[str]:
        ts = time.monotonic() if ts is None else ts
        v = self._smooth(value)

        # Determine thresholds for hysteresis
        enter_low = self.low_threshold
        exit_low = (self.low_threshold + self.hysteresis) if self.low_threshold is not None else None
        enter_high = self.high_threshold
        exit_high = (self.high_threshold - self.hysteresis) if self.high_threshold is not None else None

        # Normal -> low/high detection
        if self._state == "normal":
            if enter_low is not None and v <= enter_low:
                self._cross_start_ts = ts if self._cross_start_ts is None else self._cross_start_ts
                if (ts - self._cross_start_ts) >= self.min_duration_s and (ts - self._last_event_ts["enter_low"]) >= self.cooldown_s:
                    self._state = "low"
                    self._cross_start_ts = None
                    self._emit("enter_low", v, ts)
                    return "enter_low"
            elif enter_high is not None and v >= enter_high:
                self._cross_start_ts = ts if self._cross_start_ts is None else self._cross_start_ts
                if (ts - self._cross_start_ts) >= self.min_duration_s and (ts - self._last_event_ts["enter_high"]) >= self.cooldown_s:
                    self._state = "high"
                    self._cross_start_ts = None
                    self._emit("enter_high", v, ts)
                    return "enter_high"
            else:
                self._cross_start_ts = None

        # Low -> normal transition using exit_low
        elif self._state == "low":
            if exit_low is not None and v >= exit_low:
                self._cross_start_ts = ts if self._cross_start_ts is None else self._cross_start_ts
                if (ts - self._cross_start_ts) >= self.min_duration_s and (ts - self._last_event_ts["exit_low"]) >= self.cooldown_s:
                    self._state = "normal"
                    self._cross_start_ts = None
                    self._emit("exit_low", v, ts)
                    return "exit_low"
            else:
                self._cross_start_ts = None

        # High -> normal transition using exit_high
        elif self._state == "high":
            if exit_high is not None and v <= exit_high:
                self._cross_start_ts = ts if self._cross_start_ts is None else self._cross_start_ts
                if (ts - self._cross_start_ts) >= self.min_duration_s and (ts - self._last_event_ts["exit_high"]) >= self.cooldown_s:
                    self._state = "normal"
                    self._cross_start_ts = None
                    self._emit("exit_high", v, ts)
                    return "exit_high"
            else:
                self._cross_start_ts = None

        return None


class MultiSensorMonitor:
    """
    Holds a ThresholdBandMonitor per sensor, given a thresholds map:

        thresholds = {
          "soil_moisture": {"low": 30.0, "high": 80.0, "hysteresis": 2.0},
          "temperature_c": {"low": 15.0, "high": 30.0, "hysteresis": 0.5},
        }

    The on_event callback receives: sensor_name, event_type, value
    """

    def __init__(
        self,
        thresholds: Dict[str, Dict[str, float]],
        *,
        smoothing_alpha: float = 0.2,
        min_duration_s: float = 0.5,
        cooldown_s: float = 2.0,
        on_event: Optional[Callable[[str, str, float], None]] = None,
    ) -> None:
        self._monitors: Dict[str, ThresholdBandMonitor] = {}
        self._on_event = on_event

        for sensor_name, cfg in thresholds.items():
            monitor = ThresholdBandMonitor(
                low_threshold=cfg.get("low"),
                high_threshold=cfg.get("high"),
                hysteresis=cfg.get("hysteresis", 0.0),
                smoothing_alpha=smoothing_alpha,
                min_duration_s=min_duration_s,
                cooldown_s=cooldown_s,
                on_event=self._wrap(sensor_name),
            )
            self._monitors[sensor_name] = monitor

    def _wrap(self, sensor_name: str) -> Callable[[str, float, float], None]:
        def _handler(event_type: str, value: float, ts: float) -> None:
            if self._on_event is not None:
                self._on_event(sensor_name, event_type, value)
        return _handler

    def update(self, readings: Dict[str, float]) -> Dict[str, Optional[str]]:
        """Update monitors with a batch of sensor readings.
        Returns a dict mapping sensor_name -> last_event_type or None.
        """
        events: Dict[str, Optional[str]] = {}
        for name, value in readings.items():
            monitor = self._monitors.get(name)
            if monitor is None:
                continue
            event = monitor.update(value)
            events[name] = event
        return events

    def get_monitor(self, sensor_name: str) -> Optional[ThresholdBandMonitor]:
        return self._monitors.get(sensor_name)

