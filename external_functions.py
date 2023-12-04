from datetime import datetime, timedelta


def create_local_datetime(datetime_string_iso_8601: str) -> datetime | None:
	try:
		return datetime.fromisoformat(datetime_string_iso_8601)

	except Exception as e:
		return None


def calculate_delays(current_speed: float, stop_times: list = None) -> list | None:
	"""This function is used in order to calculate delay predictions for all upcoming stops based on the current speed of the vehicle and the distance until the next stop. The algorithm in the current form
	solves this problem by assuming linear speed until the next stop. After calculating the timespan in seconds, we propagate it to each following stop arrival and departure provided in the input variable
	stop_times
	:param float current_speed: Current speed of the vehicle in meters per second
	:param list|None stop_times: Provided stop_times of the trip we request to calculate the delays. Ordered list of dictionaries based on their stop_sequence. Each one contains the fields: 'stoshape_dist_traveled',
	'arrival_time', 'departure_time'

	:return list|None: List of vehicles found in the database based on the filters provided."""

	# If None, our final output is None as well
	if stop_times is None or len(stop_times) == 0:
		return None

	# Retrieving the distance until the next upcoming stop
	next_stop_distance = stop_times[0]['shape_dist_traveled']

	# Speed to be used for the calculation is the current speed if larger than 10
	speed_to_use = min(float(current_speed), 10)

	# Calculating the time in seconds until the first next stop
	time_until_next_stop = round(next_stop_distance/speed_to_use,2)

	# Add for each stop the time_until_next_stop
	for next_stop in stop_times:
		next_stop['arrival'] = next_stop['arrival_time'] + timedelta(seconds=time_until_next_stop)
		next_stop['departure'] = next_stop['departure_time'] + timedelta(seconds=time_until_next_stop)

	# Returning the updated stop_times of the trip
	return stop_times