from .classes.GTFSRealtimeClasses import FeedMessage, VehiclePositionEntity, TripUpdateEntity, Alert
from google.protobuf.json_format import MessageToJson, Parse, MessageToDict, ParseDict
import json


class RealTimeGTFSConstructor:
	"""This class is responsible for generating a complete gtfs realtime feed in Protobuf format as the standard requires."""

	def __init__(self):
		# Creating the message
		self.message = FeedMessage()

		# Specifying the fields of interest
		self.fields_to_collect = ['trip_id', 'route_id', 'agency_id']

		# Creating the dictionary to store all metadata
		self.metadata = {
			'trip_ids': [],
			'route_ids': [],
			'agency_ids': [],
		}

	def __collect_metadata(self, entity_data: dict):
		"""Collects the required metadata as specified in the constructor for the given feed_type, and the provided entity_data dictionary by updating the class variable 'metadata'

		:param dict entity_data: Dictionary in the structure that each different Feed in gtfs realtime is structured. More info available in the gtfs reference"""

		# Collecting all the metadata
		for field in self.fields_to_collect:
			if field in entity_data:
				self.metadata[field + 's'].append(entity_data[field])

	def __finalize_metadata(self):
		"""Updates all stored metadata id(s) by merging them in a continuous string space seperated, since this is needed in order to query the metadata in the NOSQL database."""
		for data in self.metadata:
			self.metadata[data] = ' '.join([str(x) for x in self.metadata[data]])

	def generate_avl_feed(self, data_of_entities: list, is_differential: bool = False) -> FeedMessage | None:
		"""Populates VehiclePositionEntity objects with the provided data and appends them in the message.
		:param list data_of_entities: List of entities that should be used in order to generate the feed.
		:param bool is_differential: Optional. Default is False. If True, the feed will have the differential marking in the header.

		:return FeedMessage: The constructed Vehicle Locations FeedMessage in protobuf format"""
		# if no data is available we return null output
		if len(data_of_entities) == 0: return None

		for entity_data in data_of_entities:
			self.message.message.entity.append(VehiclePositionEntity(data_of_entity=entity_data).entity)

			# Collecting metadata
			self.__collect_metadata(entity_data=entity_data)

		# Populating the header
		self.message.populate_header(is_differential=is_differential)

		# Finalizing the metadata
		self.__finalize_metadata()

		return self.message

	def generate_trip_updates_feed(self, data_of_entities: list, is_differential: bool = False) -> FeedMessage | None:
		"""Populates VehiclePositionEntity objects with the provided data and appends them in the message.
		:param list data_of_entities: List of entities that should be used in order to generate the feed.
		:param bool is_differential: Optional. Default is False. If True, the feed will have the differential marking in the header.

		:return FeedMessage: The constructed Trip Updates FeedMessage in protobuf format"""
		# if no data is available we return null output
		if len(data_of_entities) == 0: return None

		for entity_data in data_of_entities:

			# Appending each TripUpdate entity
			self.message.message.entity.append(TripUpdateEntity(data_of_entity=entity_data['entity_data'], stop_times_predictions=entity_data['stop_times_predictions']).entity)

			# Collecting metadata
			self.__collect_metadata(entity_data=entity_data['entity_data'])

		# Populating the header
		self.message.populate_header(is_differential=is_differential)

		# Finalizing the metadata
		self.__finalize_metadata()

		return self.message

	def generate_service_alerts_feed(self, data_of_entities: list, is_differential: bool = False) -> FeedMessage | None:
		"""Populates Alert objects with the provided data and appends them in the message.
		:param list data_of_entities: List of entities that should be used in order to generate the feed.
		:param bool is_differential: Optional. Default is False. If True, the feed will have the differential marking in the header.

		:return FeedMessage: The constructed Trip Updates FeedMessage in protobuf format"""
		# if no data is available we return null output
		if len(data_of_entities) == 0: return None

		for entity_data in data_of_entities:

			# Appending each TripUpdate entity
			self.message.message.entity.append(Alert(data_of_entity=entity_data).entity)

			# Collecting metadata
			self.__collect_metadata(entity_data=entity_data)

		# Populating the header
		self.message.populate_header(is_differential=is_differential)

		# Finalizing the metadata
		self.__finalize_metadata()

		return self.message

	def protobuf_to_json(self, message: FeedMessage = None) -> json:
		"""Converts a FeedMessage Protobuf object to json. If no message is provided, the self variable of message is going to be used.
		:param bool message: Optional. Default is None. If a message is provided this is the one to be used.

		:return FeedMessage: A JSON version of the message"""
		if message:
			return MessageToJson(message=message, including_default_value_fields=False, preserving_proto_field_name=True, ensure_ascii=True)
		return MessageToJson(message=self.message.message, including_default_value_fields=False, preserving_proto_field_name=True, ensure_ascii=True)

	@staticmethod
	def json_to_protobuf(json_text: str) -> FeedMessage:
		"""Converts a JSON to a Protobuf FeedMessage. If no message is provided, the self variable of message is going to be used.
		:param str json_text: Optional. Default is None. If a message is provided this is the one to be used.

		:return FeedMessage: A JSON version of the message"""
		return Parse(message=FeedMessage().message, text=json_text)

	def protobuf_to_dict(self, message: FeedMessage = None) -> dict:
		"""Converts a FeedMessage Protobuf object to dictionary. If no message is provided, the self variable of message is going to be used.
		:param FeedMessage message: Optional. Default is None. If provided, this is the Protobuf file to be converted in a dictionary instead of the one stored in the message class variable

		:return FeedMessage: A JSON version of the message"""
		if message:
			return MessageToDict(message, including_default_value_fields=False, preserving_proto_field_name=True)
		return MessageToDict(self.message.message, including_default_value_fields=False, preserving_proto_field_name=True)

	@staticmethod
	def dict_to_protobuf(dictionary: dict) -> FeedMessage:
		"""Converts a FeedMessage Protobuf object to dictionary.
		:param dict dictionary: Dictionary form of a Protobuf FeedMessage

		:return FeedMessage: Protobuf FeedMessage"""
		return ParseDict(message=FeedMessage().message, js_dict=dictionary)

	@staticmethod
	def json_to_dict(json_text: str) -> dict:
		"""Converts a JSON in string format to dictionary.
		:param str json_text: JSON in string form of a Protobuf FeedMessage

		:return FeedMessage: Protobuf FeedMessage"""
		return json.loads(json_text)