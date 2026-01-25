import api_util_firebase as fu
import api_util_general as gu
import api_util_openai as ou
import streamlit as st
from exceptions import (
    OpenAIError,
    BadRequestError,
    UserNotFoundError,
    DBError,
)


class users:

    # Keep inner classes for backward compatibility during transition
    UserNotFound = UserNotFoundError
    UserHashNotFound = UserNotFoundError
    BadRequest = BadRequestError
    OpenAIError = OpenAIError
    DBError = DBError

    def __init__(self):
        self.db = fu.firestore_db()

    def find_user(self, user_string):
        user_hash = gu.hash_user_string(user_string)
        user = self.db.get_doc(collection_name="users", document_id=user_hash)
        if user:
            return user
        else:
            raise UserNotFoundError("User not found")

    def get_user(self, user_id):
        user = self.db.get_doc(collection_name="users", document_id=user_id)
        if user:
            return user
        else:
            raise UserNotFoundError("User not found")

    def get_users(self, user_hash=None):
        query_filters=[]

        if user_hash:
            query_filters = [("user_hash","==",user_hash)]

        user_docs = self.db.get_docs(collection_name="users", query_filters=query_filters)

        return user_docs


    def update_user_stats(self, user_id, metric_value_pairs):
        user = self.get_user(user_id)

        if not user:
            raise UserNotFoundError("User not found")

        if metric_value_pairs == None:
            raise BadRequestError("Bad request: need to supply (metric, value) pairs")

        for metric_value_pair in metric_value_pairs:
            try:
                float(str(metric_value_pair[1]))
            except ValueError:
                raise BadRequestError("Bad request: need numeric values")

        for metric_value_pair in metric_value_pairs:
            self.db.increment_document_fields(collection_name="users", document_id=user_id, field_name=metric_value_pair[0], increment=metric_value_pair[1])


    def create_user(self, user_hash):
        user = self.get_users(user_hash=user_hash)

        if len(user) > 0:
            raise BadRequestError("Bad request: user exists")

        user_dict = {
            'user_hash': user_hash,
            'created_date': gu.get_current_time(),
            'last_modified_date': gu.get_current_time()
        }

        user_id = self.db.create_doc(collection_name="users",data=user_dict)
        return user_id


    def find_user_hash(self, user_hash):
        user_hash_doc = self.db.get_doc(collection_name="user_hash", document_id=user_hash)
        if user_hash_doc:
            return user_hash_doc
        else:
            raise UserNotFoundError("User Hash not found")


    def create_user_hash(self, user_hash):
        try:
            self.find_user_hash(user_hash=user_hash)
            raise BadRequestError("Bad request: user hash exists")
        except UserNotFoundError:
            pass

        user_hash_dict = {
            'user_hash_type': 'open_ai_key',
            'created_date': gu.get_current_time()
        }

        user_hash_id = self.db.create_doc(collection_name="user_hash",data=user_hash_dict, id=user_hash)
        return user_hash_id


    def get_create_user(self, api_key):
        o = ou.open_ai(api_key=api_key, restart_sequence='|USER|', stop_sequence='|SP|')
        validation_info = o.validate_key()
        supported_models_list = validation_info['supported_models_list']

        user_hash = gu.hash_user_string(api_key)

        # first try to create a user_hash document using the hashed key
        try:
            self.create_user_hash(user_hash=user_hash)
        except BadRequestError:
            # swallows exception if user hash already exists
            pass

        try:
            # create a user with user hash
            user_id = self.create_user(user_hash=user_hash)
            # get user details
            user = self.get_user(user_id=user_id)

        except BadRequestError:
            # since user exists, just get user details
            user = self.get_users(user_hash=user_hash)

            if len(user) > 1:
                raise BadRequestError("Bad request: more than one user with API key")
            user = user[0]

        # Add the supported models list to the user object
        user['data']['supported_models_list'] = supported_models_list

        return user
