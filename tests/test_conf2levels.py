import argparse
import os
import tempfile

import pytest

from conf2levels import (
    ArgparseReader,
    ConfigReader,
    ConfigValueError,
    DictionaryReader,
    EnvironReader,
    IniReader,
    ReaderBase,
    ReaderSelector,
    load_readers_by_keyword,
    validate_key,
)
from conf2levels.exceptions import IniReaderError

FILES_DIR = os.path.join(os.path.dirname(__file__), "files")

# [Classical]
# name = Mozart

# [Romantic]
# name = Schumann
INI_FILE = os.path.join(FILES_DIR, "config.ini")

os.environ["XXX__Classical__name"] = "Mozart"
os.environ["XXX__Baroque__name"] = "Bach"

parser = argparse.ArgumentParser()
parser.add_argument("--classical-name")
parser.add_argument("--baroque-name")
ARGPARSER_NAMESPACE = parser.parse_args(
    ["--baroque-name", "Bach", "--classical-name", "Mozart"]
)


class TestFunctionValidateKey:
    def test_valid(self) -> None:
        assert validate_key("test")
        assert validate_key("test_1")
        assert validate_key("1")
        assert validate_key("a")
        assert validate_key("ABC_abc_123")

    def test_invalid(self) -> None:
        with pytest.raises(ValueError) as context:
            validate_key("l o l")
        assert (
            context.value.args[0] == "The key “l o l” contains invalid characters "
            "(allowed: a-zA-Z0-9_)."
        )
        with pytest.raises(ValueError) as context:
            validate_key("ö")


# Reader classes ##############################################################


class FalseReader(ReaderBase):
    def not_get(self) -> str:
        return "It’s not get"


class TestClassReaderBase:
    def test_exception(self) -> None:
        with pytest.raises(TypeError):
            FalseReader()  # type: ignore


class TestClassArgparseReader:
    def test_method_get_without_mapping(self) -> None:
        argparse = ArgparseReader(args=ARGPARSER_NAMESPACE)
        assert argparse.get("Classical", "name") == "Mozart"
        assert argparse.get("Baroque", "name") == "Bach"

    def test_method_get_with_mapping(self) -> None:
        argparse = ArgparseReader(
            args=ARGPARSER_NAMESPACE,
            mapping={
                "Classical.name": "classical_name",
                "Baroque.name": "baroque_name",
            },
        )
        assert argparse.get("Classical", "name") == "Mozart"
        assert argparse.get("Baroque", "name") == "Bach"

    def test_exception(self) -> None:
        argparse = ArgparseReader(
            args=ARGPARSER_NAMESPACE,
            mapping={
                "Classical.name": "classical_name",
                "Baroque.name": "baroque_name",
                "Romantic.name": "romantic_name",
            },
        )
        with pytest.raises(ConfigValueError):
            argparse.get("Romantic", "name")

        with pytest.raises(ConfigValueError):
            argparse.get("Modern", "name")


class TestClassDictionaryReader:
    dictionary = {"Classical": {"name": "Mozart"}}

    def test_method_get(self) -> None:
        dictionary = DictionaryReader(dictionary=self.dictionary)
        assert dictionary.get("Classical", "name") == "Mozart"

    def test_exception(self) -> None:
        dictionary = DictionaryReader(dictionary=self.dictionary)
        with pytest.raises(ConfigValueError):
            dictionary.get("Romantic", "name")


class TestClassEnvironReader:
    def test_method_get(self) -> None:
        os.environ["AAA__bridge__ip"] = "1.2.3.4"
        os.environ["AAA__bridge__username"] = "test"
        environ = EnvironReader(prefix="AAA")
        assert environ.get("bridge", "ip") == "1.2.3.4"
        assert environ.get("bridge", "username") == "test"

    def test_exception(self) -> None:
        environ = EnvironReader(prefix="AAA")
        with pytest.raises(ConfigValueError) as context:
            environ.get("lol", "lol")
        assert context.value.args[0] == "Environment variable not found: AAA__lol__lol"


class TestClassEnvironWithoutPrefix:
    def test_method_get(self) -> None:
        os.environ["Avantgarde__name"] = "Stockhausen"
        environ = EnvironReader()
        assert environ.get("Avantgarde", "name") == "Stockhausen"
        del os.environ["Avantgarde__name"]

    def test_exception(self) -> None:
        environ = EnvironReader()
        with pytest.raises(ConfigValueError) as context:
            environ.get("xxxAvantgarde", "xxxname")
        assert (
            context.value.args[0]
            == "Environment variable not found: xxxAvantgarde__xxxname"
        )


class TestClassIniReader:
    def test_method_get(self) -> None:
        ini = IniReader(path=INI_FILE)
        assert ini.get("Classical", "name") == "Mozart"
        assert ini.get("Romantic", "name") == "Schumann"

    def test_exception(self) -> None:
        ini = IniReader(path=INI_FILE)
        with pytest.raises(ConfigValueError) as context:
            ini.get("lol", "lol")
        assert (
            context.value.args[0]
            == "Configuration value could not be found (section “lol” key "
            "“lol”)."
        )

    def test_non_existent_ini_file(self) -> None:
        tmp_path = tempfile.mkdtemp()
        non_existent = os.path.join(tmp_path, "xxx")
        with pytest.raises(IniReaderError):
            IniReader(path=non_existent)

    def test_none(self) -> None:
        with pytest.raises(IniReaderError):
            IniReader(path=None)  # type: ignore

    def test_false(self) -> None:
        with pytest.raises(IniReaderError):
            IniReader(path=False)  # type: ignore

    def test_emtpy_string(self) -> None:
        with pytest.raises(IniReaderError):
            IniReader(path="")


# Common code #################################################################


class TestClassReaderSelector:
    def test_ini_first(self) -> None:
        reader = ReaderSelector(IniReader(INI_FILE), EnvironReader(prefix="XXX"))
        assert reader.get("Classical", "name") == "Mozart"

    def test_environ_first(self) -> None:
        reader = ReaderSelector(EnvironReader("XXX"), IniReader(INI_FILE))
        assert reader.get("Baroque", "name") == "Bach"

    def test_exception(self) -> None:
        reader = ReaderSelector(EnvironReader("XXX"), IniReader(INI_FILE))
        with pytest.raises(ValueError) as context:
            reader.get("lol", "lol")
        assert (
            context.value.args[0]
            == "Configuration value could not be found (section “lol” key "
            "“lol”)."
        )


class TestFunctionLoadReadersByKeyword:
    def test_without_keywords_arguments(self) -> None:
        with pytest.raises(TypeError):
            load_readers_by_keyword(INI_FILE, "XXX")  # type: ignore

    def test_order_ini_environ(self) -> None:
        readers = load_readers_by_keyword(ini=INI_FILE, environ="XXX")
        assert readers[0].__class__.__name__ == "IniReader"
        assert readers[1].__class__.__name__ == "EnvironReader"

    def test_order_environ_ini(self) -> None:
        readers = load_readers_by_keyword(
            environ="XXX",
            ini=INI_FILE,
        )
        assert readers[0].__class__.__name__ == "EnvironReader"
        assert readers[1].__class__.__name__ == "IniReader"

    def test_argparse_single_arguemnt(self) -> None:
        readers = load_readers_by_keyword(argparse=ARGPARSER_NAMESPACE)
        assert readers[0].__class__.__name__ == "ArgparseReader"


# Integration tests ###########################################################


class TestClassConfigReader:
    def setup_method(self) -> None:
        # argparser
        parser = argparse.ArgumentParser()
        parser.add_argument("--common-key")
        parser.add_argument("--specific-argparse")
        args = parser.parse_args(
            ["--common-key", "argparse", "--specific-argparse", "argparse"]
        )
        self.argparse = (
            args,
            {"common.key": "common_key", "specific.argparse": "specific_argparse"},
        )
        # dictionary
        self.dictionary = {
            "common": {"key": "dictionary"},
            "specific": {"dictionary": "dictionary"},
        }

        # environ
        self.environ = "YYY"
        os.environ["YYY__common__key"] = "environ"
        os.environ["YYY__specific__environ"] = "environ"

        # ini
        self.ini = os.path.join(FILES_DIR, "integration.ini")

    def teardown_method(self) -> None:
        del os.environ["YYY__common__key"]
        del os.environ["YYY__specific__environ"]

    def test_argparse_first(self) -> None:
        conf2levels = ConfigReader(
            argparse=self.argparse,
            dictionary=self.dictionary,
            environ=self.environ,
            ini=self.ini,
        )
        config = conf2levels.get_class_interface()
        assert config.common.key == "argparse"

    def test_argparse_empty(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--empty-key")
        args = parser.parse_args([])
        conf2levels = ConfigReader(
            argparse=(args, {}),
            dictionary={"empty": {"key": "from_dict"}},
        )
        config = conf2levels.get_class_interface()
        assert config.empty.key == "from_dict"

    def test_dictionary_first(self) -> None:
        conf2levels = ConfigReader(
            dictionary=self.dictionary,
            argparse=self.argparse,
            environ=self.environ,
            ini=self.ini,
        )
        config = conf2levels.get_class_interface()
        assert config.common.key == "dictionary"

    def test_environ_first(self) -> None:
        conf2levels = ConfigReader(
            environ=self.environ,
            argparse=self.argparse,
            dictionary=self.dictionary,
            ini=self.ini,
        )
        config = conf2levels.get_class_interface()
        assert config.common.key == "environ"

    def test_ini_first(self) -> None:
        conf2levels = ConfigReader(
            ini=self.ini,
            argparse=self.argparse,
            dictionary=self.dictionary,
            environ=self.environ,
        )
        config = conf2levels.get_class_interface()
        assert config.common.key == "ini"

    def test_specifiy_values(self) -> None:
        conf2levels = ConfigReader(
            argparse=self.argparse,
            dictionary=self.dictionary,
            environ=self.environ,
            ini=self.ini,
        )
        config = conf2levels.get_class_interface()
        assert config.specific.argparse == "argparse"
        assert config.specific.dictionary == "dictionary"
        assert config.specific.environ == "environ"
        assert config.specific.ini == "ini"

    def test_method_get_class_interface(self) -> None:
        conf2levels = ConfigReader(
            argparse=self.argparse,
            dictionary=self.dictionary,
            environ=self.environ,
            ini=self.ini,
        )
        config = conf2levels.get_class_interface()
        assert config.specific.argparse == "argparse"
        assert config.specific.dictionary == "dictionary"
        assert config.specific.environ == "environ"
        assert config.specific.ini == "ini"

    def test_method_get_dictionary_interface(self) -> None:
        conf2levels = ConfigReader(
            argparse=self.argparse,
            dictionary=self.dictionary,
            environ=self.environ,
            ini=self.ini,
        )
        config = conf2levels.get_dictionary_interface()
        assert config["specific"]["argparse"] == "argparse"
        assert config["specific"]["dictionary"] == "dictionary"
        assert config["specific"]["environ"] == "environ"
        assert config["specific"]["ini"] == "ini"

    def test_method_check_section(self) -> None:
        dictionary = {
            "missing_key": {"key": "value"},
            "all_good": {"key": "value"},
            "empty": {"key": ""},
        }
        spec = {
            "missing_key": {  # section
                "key": {  # key
                    "not_empty": True,
                },
                "not_configured_key": {  # key
                    "not_empty": False,
                },
            },
            "all_good": {  # section
                "key": {  # key
                    "not_empty": True,
                }
            },
            "empty": {  # section
                "key": {  # key
                    "not_empty": True,
                }
            },
        }
        conf2levels = ConfigReader(
            spec=spec,
            dictionary=dictionary,
        )
        assert conf2levels.check_section("all_good")
        with pytest.raises(ValueError):
            conf2levels.check_section("missing_key")
        with pytest.raises(KeyError):
            conf2levels.check_section("xxx")
        with pytest.raises(ValueError):
            conf2levels.check_section("empty")

    def test_spec_defaults(self) -> None:
        dictionary = {
            "no_default": {
                "key": "No default value",
            },
        }
        spec = {
            "default": {
                "key": {
                    "description": "A default value",
                    "default": 123,
                },
            },
            "no_default": {
                "key": {
                    "description": "No default value",
                },
            },
        }
        conf2levels = ConfigReader(
            spec=spec,
            dictionary=dictionary,
        )
        config = conf2levels.get_class_interface()
        assert config.no_default.key == "No default value"
        assert config.default.key == 123

    def test_method_spec_to_argparse(self) -> None:
        spec = {
            "email": {
                "smtp_login": {
                    "description": "The SMTP login name",
                    "default": "user1",
                },
            },
        }
        conf2levels = ConfigReader(spec=spec)
        parser = argparse.ArgumentParser()
        conf2levels.spec_to_argparse(parser)
        args = parser.parse_args([])
        assert args.email_smtp_login == "user1"
        args = parser.parse_args(["--email-smtp-login", "user2"])
        assert args.email_smtp_login == "user2"


class TestTypes:
    def setup_method(self) -> None:
        conf2levels = ConfigReader(ini=os.path.join(FILES_DIR, "types.ini"))
        self.config = conf2levels.get_class_interface()

    def test_int(self) -> None:
        assert self.config.types.int == 1

    def test_float(self) -> None:
        assert self.config.types.float == 1.1

    def test_str(self) -> None:
        assert self.config.types.str == "Some text"

    def test_list(self) -> None:
        assert self.config.types.list == [1, 2, 3]

    def test_tuple(self) -> None:
        assert self.config.types.tuple == (1, 2, 3)

    def test_dict(self) -> None:
        assert self.config.types.dict == {"one": 1, "two": 2}

    def test_code(self) -> None:
        assert self.config.types.code == "print('lol')"

    def test_invalid_code(self) -> None:
        assert self.config.types.invalid_code == "print('lol)'"

    def test_bool(self) -> None:
        assert self.config.types.bool

    def test_empty_string(self) -> None:
        assert self.config.types.empty_str == ""

    def test_none(self) -> None:
        assert self.config.types.none is None

    def test_zero(self) -> None:
        assert self.config.types.zero == 0

    def test_false(self) -> None:
        assert not self.config.types.false

    def test_false_str(self) -> None:
        assert self.config.types.false_str == "false"
