from contextlib import ExitStack
import json
import unittest
import unittest.mock as Mock

from src.models import User
import main


class TestApi(unittest.TestCase):

    def setUp(self):
        self.person = User()

        self.person.name = "Mikoaj"
        self.person.nickname = "Kwasniewski"
        self.person.age = 25
        self.person.id = 25

    def test_getInfo(self):
        test_id = 1
        Expected_value = {
            "message": f"Person has been shown "
                       f"'name = {self.person.name}, "
                       f"nickname = {self.person.nickname}, "
                       f"age = {self.person.age}'"}
        Expected_status = 200
        with ExitStack() as stack:
            # Pusty obiekt mocka udajacy rezultat session.query
            query_mock = Mock.Mock()
            # Mockuje zwrotke z funkcji filter_by()
            query_mock.filter_by.return_value = query_mock
            # Mockuje zwrotke z funkcji first() - zwraca odgornie
            # przygotowany obiekt uzytkownika self.person
            query_mock.first.return_value = self.person

            # nadpisywanie (Mockowanie) obiektu main.session odpowiedzialnego
            # za sesje z baza danych
            session_mock = stack.enter_context(Mock.patch.object(
                main, 'session', return_value=Mock.Mock()))
            # mockuje zwrotkne z session.query - wczesniej przeygotowany
            # query mock jest wynikiem tej funkcji
            session_mock.query.return_value = query_mock
            # Mockuje main.isEmpty()
            stack.enter_context(Mock.patch('main.isEmpty'))

            # Uruchomienie i porownanie odpowiedzi z zadanym wynikiem
            result, status = main.getInfo(test_id)
            self.assertEqual(result, Expected_value)
            self.assertEqual(status, Expected_status)

    def test__register(self):
        with main.app.app_context():
            Expected_content = {'name': 'Bartosz', "nickname": "Rupala", "age": 25}

            Expected_message = "person has been added"
            Expected_status = 202

            with ExitStack() as stack:
                # import pdb; pdb.set_trace()
                request_mock = stack.enter_context(Mock.patch(
                    'main.getData', return_value=Expected_content))
                request_mock.get_json.return_value = Expected_content
                stack.enter_context(Mock.patch('main.paramsValidate'))
                stack.enter_context(Mock.patch.object(main, 'session'))

                result, status = main._register()
                result = json.loads(result.response[0]).get('message')

                self.assertEqual(result, Expected_message)
                self.assertEqual(status, Expected_status)
