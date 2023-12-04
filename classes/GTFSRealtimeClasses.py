from google.transit import gtfs_realtime_pb2
from datetime import datetime

class FeedMessage:
	"""A realtime feed is always defined with relation to an existing GTFS feed and can be one of the following: Vehicle Positions, TripUpdates and Alerts. All the entity ids are resolved with respect to
	the GTFS feed. More information can be found here: https://developers.google.com/transit/gtfs-realtime/reference . In order to generate the Feed message in protobuf format, we utilize the
	gtfs_realtime_pb2 library."""
	def __init__(self):
		# Creating the message
		self.message = gtfs_realtime_pb2.FeedMessage()


	def populate_header(self, is_differential: bool = False):
		"""Version of the feed specification. The current version is 2.0.
		This timestamp identifies the moment when the content of this feed has been created (in server time).
		Determines whether the current fetch is incremental (currently, this mode is unsupported).
		:param bool is_differential: Optional. Default is False. If True, the feed will have the differential marking in the header."""

		# Updating the Metadata about the feed
		self.message.header.gtfs_realtime_version = '2.0'

		# Always setting the feed to FULL_DATASET
		self.message.header.incrementality = "DIFFERENTIAL" if is_differential else "FULL_DATASET"

		# Generating the current time in seconds (POSIX timestamp)
		self.message.header.timestamp = int(datetime.utcnow().timestamp())


class RealTimeEntity:
	def __init__(self, data_of_entity: dict):
		"""The class when initialized generates a realtime gtfs FeedEntity object. This class itself cannot be used directly in gtfs realtime. It provides a common foundation for the classes
		VehiclePositionEntity, TripUpdateEntity and Alert Entity"""
		# Initializing the ProtoBuf for the FeedEntity Object
		self.entity = gtfs_realtime_pb2.FeedEntity()

		# Initializing the time and date
		self.time = None
		self.date = None

		# Retrieving the entity's id
		self.id = data_of_entity.get('id', None)

		# Company identifier
		self.company_id = data_of_entity.get('company_id', None)

		# Generating the entity's local datetime
		self.datetime = self.create_local_datetime(datetime_string_iso_8601=data_of_entity.get('datetime', None))

		# Updating the time and date values
		self.update_time_and_date()

		# On board TT required data
		self.user_id = data_of_entity.get('user_id', None)
		self.trip_id = data_of_entity.get('trip_id', None)
		self.route_id = data_of_entity.get('route_id', None)
		self.license_plate = data_of_entity.get('license_plate', None)

		# Incase this is a frequency based field
		self.start_time = data_of_entity.get('start_time', None)
		self.start_date = data_of_entity.get('start_date', None)

		self.location = data_of_entity.get('location', None)

		# Vehicle location
		self.latitude = data_of_entity.get('latitude', None)
		self.longitude = data_of_entity.get('longitude', None)

		# Vehicle motion features
		self.heading = data_of_entity.get('heading', None)
		self.speed = data_of_entity.get('speed', None)  # meters per second
		self.speed_accuracy = data_of_entity.get('speed_accuracy', None)
		self.odometer = data_of_entity.get('odometer', None)

		# Passenger and network traffic
		self.congestion_level = data_of_entity.get('congestion_level', None)
		self.occupancy_status = data_of_entity.get('occupancy_status', None)
		self.current_stop_sequence = data_of_entity.get('stop_sequence', None)
		self.stop_id = data_of_entity.get('stop_id', None)
		self.current_status = data_of_entity.get('current_status', None)

	def update_time_and_date(self):
		"""Updates the class variables date and time by decomposing the class variable datetime."""
		self.date = str(self.datetime.date())
		self.time = str(self.datetime.time())


	@staticmethod
	def create_local_datetime(datetime_string_iso_8601: str) -> datetime | None:
		"""Used to create a datetime object from a provided iso 8601 string

		:param str datetime_string_iso_8601:  in iso 8601 format"""
		try:
			return datetime.fromisoformat(datetime_string_iso_8601)

		except Exception as e:
			return None


	def populate_trip_descriptor(self, setting: str):
		"""A descriptor that identifies a single instance of a GTFS trip.

		:param str setting: Name of the entity we are populating. Accepted values are: 'vehicle_position' and 'trip_update'."""
		if setting == 'vehicle_position':
			self.entity.vehicle.trip.trip_id = self.trip_id
			self.entity.vehicle.trip.route_id = self.route_id

			# In case this is a frequency based trip we also the start_time
			if self.start_time is not None:
				self.entity.vehicle.trip.start_time = self.start_time

		if setting == 'trip_update':
			self.entity.trip_update.trip.trip_id = self.trip_id
			self.entity.trip_update.trip.route_id = self.route_id

			# If it is a frequency based trip or a schedule based we also the start time
			if self.start_time is not None:
				self.entity.vehicle.trip.start_time = self.start_time

			# If it is a frequency based trip or a schedule based we also the start date
			if self.start_date is not None:
				self.entity.vehicle.trip.start_date = self.start_date


	def __populate_vehicle_descriptor(self, setting: str):
		"""Populates VehicleDescriptor Identification information for the vehicle performing the trip.

		:param str setting: Name of the entity we are populating. Accepted values are: 'vehicle_position' and 'trip_update'."""
		if setting == 'vehicle_position':
			if self.license_plate is not None:
				self.entity.vehicle.vehicle.license_plate = self.license_plate
				# self.entity.vehicle.vehicle.label = None

		if setting == 'trip_update':
			self.entity.trip_update.vehicle.label = None
			self.entity.trip_update.vehicle.license_plate = None


class VehiclePositionEntity(RealTimeEntity):
	def __init__(self, data_of_entity: dict = None):
		"""The VehicleRealTimeEntity is an Entity of a Vehicle's location at a specific time."""
		super().__init__(data_of_entity=data_of_entity)

		# Populating the entity's data
		self.__populate_entity()


	def __populate_position(self):
		"""Populates the geographic position of a vehicle."""
		# Updating the vehicle's position
		self.entity.vehicle.position.latitude = self.latitude
		self.entity.vehicle.position.longitude = self.longitude
		self.entity.vehicle.position.odometer = self.odometer
		self.entity.vehicle.position.speed = self.speed

	def __populate_entity(self):
		"""Populates the VehiclePositionEntity."""
		# Update the entity's id
		self.entity.id = self.id

		# Populate the Vehicle Descriptor
		self.__populate_position()

		# Populate the Trip Descriptor
		self.populate_trip_descriptor(setting='vehicle_position')

		# Update occupancy and congestion
		self.entity.vehicle.occupancy_status = self.occupancy_status if self.occupancy_status is not None else ""
		self.entity.vehicle.congestion_level = self.congestion_level if self.congestion_level is not None else ""

		if self.current_stop_sequence is not None:
			# Update the current stop_id and stop_sequence which is going to be serviced at
			self.entity.vehicle.current_stop_sequence = self.current_stop_sequence

		self.entity.vehicle.stop_id = self.stop_id if self.stop_id is not None else ""

		self.entity.vehicle.current_status = self.current_status

class TripUpdateEntity(RealTimeEntity):
	def __init__(self, data_of_entity, stop_times_predictions):
		"""The TripUpdateEntity is a Realtime update on the progress of a vehicle along a trip. Please also refer to the general discussion of the trip updates entities."""
		super().__init__(data_of_entity=data_of_entity)

		# Populating the stop_time predictions
		self.stop_times_predictions = stop_times_predictions

		# Populating the entity
		self.__populate_entity()


	def __populate_stop_time_update(self, stop_time_data: dict):
		"""Populates StopTimeUpdate entity"""
		stop_time_update = gtfs_realtime_pb2.TripUpdate().StopTimeUpdate()
		stop_time_update.stop_sequence = stop_time_data['stop_sequence']
		stop_time_update.stop_id = str(stop_time_data['stop_id'])
		stop_time_update.arrival.delay = stop_time_data['arrival'].seconds
		stop_time_update.departure.delay  = stop_time_data['departure'].seconds
		return stop_time_update


	def __populate_stop_times(self):
		"""Populates StopTimeUpdate placeholder containing all future stop timing predictions"""
		if self.stop_times_predictions is None:
			return

		# Iterating over each follow-up stop
		for stop_time_data in self.stop_times_predictions:
			self.entity.trip_update.stop_time_update.append(self.__populate_stop_time_update(stop_time_data=stop_time_data))


	def __populate_entity(self):
		"""Populates the TripUpdateEntity"""
		# Update the entity's id
		self.entity.id = self.id

		# Populate the Trip Descriptor
		self.populate_trip_descriptor(setting='trip_update')

		# Populating stop times
		self.__populate_stop_times()


class Alert:
	def __init__(self, data_of_entity: dict = None):
		"""The TripUpdateEntity is a Realtime update on the progress of a vehicle along a trip. Please also refer to the general discussion of the trip updates entities."""
		# Retrieving the entity's id
		self.id = data_of_entity.get('id', None)

		# Initializing the ProtoBuf for the FeedEntity Object
		self.entity = gtfs_realtime_pb2.FeedEntity()

		self.time_periods = data_of_entity.get('time_periods', None)

		# EntitySelector class variables
		self.selected_entities = data_of_entity.get('selected_entities', None)

		# Trip Descriptor data
		self.trip_data = data_of_entity.get('trip_data', None)

		# Additional information about the alert.
		self.cause = data_of_entity.get('cause', None)
		self.effect = data_of_entity.get('effect', None)
		self.url_data = data_of_entity.get('url_data', None)
		self.header_text_data = data_of_entity.get('header_text_data', None)
		self.description_text_data = data_of_entity.get('description_text_data', None)

		# Populating the entity
		self.__populate_entity()

	@staticmethod
	def __generate_entity_selector():
		return gtfs_realtime_pb2.EntitySelector()


	@staticmethod
	def __generate_translation(data: dict):
		# Generating an empty translation
		temp_translation = gtfs_realtime_pb2.TranslatedString().Translation()
		temp_translation.text = data['text']
		temp_translation.language = data['language']

		# Returning the data
		return temp_translation


	def __populate_url(self):
		for text_data in self.url_data:
			# Generating the translation text and appending it
			self.entity.alert.url.translation.append(self.__generate_translation(text_data))


	def __populate_header_text(self):
		for text_data in self.header_text_data:
			# Generating the translation text and appending it
			self.entity.alert.header_text.translation.append(self.__generate_translation(text_data))


	def __populate_description_text(self):
		for text_data in self.description_text_data:
			# Generating the translation text and appending it
			self.entity.alert.header_text.translation.append(self.__generate_translation(text_data))


	def __populate_trip_entity(self, data: dict):
		# Generating an empty entity selector
		temp_selector = self.__generate_entity_selector()

		# Populating the entity
		if data.get('trip_id', None) is not None:
			temp_selector.trip.trip_id = data['trip_id']

		if data.get('route_id', None) is not None:
			temp_selector.trip.route_id = data['route_id']

		if data.get('start_time', None) is not None:
			temp_selector.trip.start_time = data['start_time']

		if data.get('start_date', None) is not None:
			temp_selector.trip.start_date = data['start_date']

		return temp_selector


	def populate_selected_entities(self):
		temp_output = []
		for entity_type in self.selected_entities:

			# Appending the data
			temp_output += self.populate_entity_selector(entity_type=entity_type, data=self.selected_entities[entity_type])

		for item in temp_output:
			self.entity.alert.informed_entity.append(item)

	def populate_entity_selector(self, entity_type: str, data: dict):

		output = []
		if entity_type == 'routes':
			for item in data:
				# Generating an empty entity selector
				temp_selector = self.__generate_entity_selector()

				# Populating the entity
				temp_selector.route_id = str(item)

				output.append(temp_selector)

		elif entity_type == 'agencies':

			for item in data:
				# Generating an empty entity selector
				temp_selector = self.__generate_entity_selector()

				# Populating the entity
				temp_selector.agency_id = str(item)

				output.append(temp_selector)

		elif entity_type == 'route_types':

			for item in data:
				# Generating an empty entity selector
				temp_selector = self.__generate_entity_selector()

				# Populating the entity
				temp_selector.route_type = int(item)

				output.append(temp_selector)

		elif entity_type == 'trips':

			for item in data:
				output.append(self.__populate_trip_entity(data=item))
		else:
			return []

		return output


	def __populate_time_ranges(self):
		for interval in self.time_periods:

			# Generating the time range
			time_range = gtfs_realtime_pb2.TimeRange()

			# Populating the start and end
			time_range.start = interval['start']
			time_range.end = interval['end']

			# Appending the time range
			self.entity.alert.active_period.append(time_range)

	def __populate_cause_and_effect(self):

		self.entity.alert.cause = self.cause
		self.entity.alert.effect = self.effect


	def __populate_entity(self):
		"""Populates the TripUpdateEntity"""
		# Update the entity's id
		self.entity.id = self.id

		# Populate the Time range
		self.__populate_time_ranges()

		# Populating the affected entities
		self.populate_selected_entities()

		# Populating the cause and the effect
		self.__populate_cause_and_effect()

		# Populating the url
		self.__populate_url()

		# Populating the header text
		self.__populate_header_text()

		# Populating the description text
		self.__populate_description_text()