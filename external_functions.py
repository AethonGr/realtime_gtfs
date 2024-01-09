from datetime import datetime, timedelta
import math

def create_local_datetime(datetime_string_iso_8601: str) -> datetime | None:
	try:
		return datetime.fromisoformat(datetime_string_iso_8601)

	except Exception as e:
		return None


def calculate_delays(current_speed: float, current_acceleration: float = None, stop_times: list = None, add_delay_to_stop_times: bool = True) -> list | None:
	"""This function is used in order to calculate delay predictions for all upcoming stops based on the current speed of the vehicle and the distance until the next stop. The algorithm in the current form
	solves this problem by assuming linear speed until the next stop. After calculating the timespan in seconds, we propagate it to each following stop arrival and departure provided in the input variable
	stop_times
	:param bool add_delay_to_stop_times: Optional. Default is True. If True, the delay is going to be added to the stop_times. If False, the delay is going to be returned as a list of floats.
	:param float current_speed: Current speed of the vehicle in meters per second (average)
	:param float current_acceleration: Current acceleration of the vehicle in meters per second squared (average)
	:param list|None stop_times: Provided stop_times of the trip we request to calculate the delays. Ordered list of dictionaries based on their stop_sequence. Each one contains the fields: 'stoshape_dist_traveled',
	:bool add_delay_to_stop_times: Optional. Default is True. If True, the delay is going to be added to the stop_times. If False, the delay is going to be returned as a list of floats.
	'arrival_time', 'departure_time'

	:return list|None: The updated stop_times of the trip with the calculated delays. If the input stop_times is None or empty, the output is None as well."""

	# If None, our final output is None as well
	if stop_times is None or len(stop_times) == 0:
		return None

	# Retrieving the distance until the next upcoming stop
	next_stop_distance = stop_times[0]['shape_dist_traveled']

	lower_limit = 10  # Minimum speed limit
	upper_limit = 100  # Maximum speed limit
	speed_to_use = max(lower_limit, min(upper_limit, current_speed))  # Apply limits

	# Re-adjust the current acceleration
	current_acceleration = current_acceleration if round(current_acceleration) != 0 else None
	if current_acceleration is None:
		# Calculating the time in seconds until the first next stop
		time_until_next_stop = next_stop_distance/speed_to_use
	else:
		# Calculating the time in seconds until the first next stop using the Uniformly Accelerated Motion from Rest formula
		time_until_next_stop = math.sqrt((2 * next_stop_distance) / float(current_acceleration))

	# Round the time_until_next_stop to 2 decimal places
	time_until_next_stop = round(time_until_next_stop)

	# If we don't want to add the delay to the stop_times, we return the delay
	if not add_delay_to_stop_times:
		for next_stop in stop_times:
			next_stop['delay'] = time_until_next_stop

	else:
		# Add for each stop the time_until_next_stop
		for next_stop in stop_times:
			next_stop['arrival'] = next_stop['arrival_time'] + timedelta(seconds=time_until_next_stop)
			next_stop['departure'] = next_stop['departure_time'] + timedelta(seconds=time_until_next_stop)
			next_stop['delay'] = time_until_next_stop
	# Returning the updated stop_times of the trip
	return stop_times