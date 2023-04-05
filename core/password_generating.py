from secrets import choice

from re import compile

from typing import Tuple

from core.config import password_parameters


class GeneratedPassword(object):
    def __init__(self,
                 length: int = password_parameters.RECOMMENDED_LENGTH,
                 uppercase: bool = False,
                 lowercase: bool = False,
                 digits: bool = False,
                 math: bool = False,
                 underscore: bool = False,
                 punctuation: bool = False,
                 special: bool = False,
                 brackets: bool = False):

        self.alphabet: str = ''
        self.length: int = length
        self.password: str = ''
        self.recommendations: list[str] = []

        self.uppercase: bool = uppercase
        self.lowercase: bool = lowercase
        self.digits: bool = digits
        self.math: bool = math
        self.underscore: bool = underscore
        self.punctuation: bool = punctuation
        self.special: bool = special
        self.brackets: bool = brackets

    def accumulate_alphabet_by_conditions(self) -> str:
        if self.lowercase:
            self.alphabet += password_parameters.LOWER_CASE
        if self.uppercase:
            self.alphabet += password_parameters.UPPER_CASE
        if self.digits:
            self.alphabet += password_parameters.DIGITS
        if self.math:
            self.alphabet += password_parameters.MATH
        if self.underscore:
            self.alphabet += password_parameters.UNDERSCORE
        if self.punctuation:
            self.alphabet += password_parameters.PUNCTUATION
        if self.special:
            self.alphabet += password_parameters.SPECIAL
        if self.brackets:
            self.alphabet += password_parameters.BRACKETS
        if not self.alphabet:
            self.accumulate_alphabet()
        return self.alphabet

    def accumulate_alphabet(self) -> str:
        self.alphabet += password_parameters.LOWER_CASE + password_parameters.UPPER_CASE + \
                         password_parameters.DIGITS + password_parameters.MATH + password_parameters.UNDERSCORE + \
                         password_parameters.PUNCTUATION + password_parameters.SPECIAL + password_parameters.BRACKETS
        return self.alphabet

    def set_password(self, new_password: str):
        self.password = new_password
        self.recommendations.clear()
        self.get_recommendations()
        return

    def generate_password(self) -> str:
        self.recommendations.clear()
        if not self.alphabet:
            self.accumulate_alphabet()
        while self.password_is_secure() is False:
            self.password = ''.join(choice(self.alphabet) for _ in range(self.length))
        return self.password

    def generate_password_optional(self) -> str:
        self.recommendations.clear()
        if self.alphabet == '':
            self.accumulate_alphabet()
        self.password = ''.join(choice(self.alphabet) for _ in range(self.length))
        return self.password

    def generate_password_by_conditions(self) -> str:
        if self.alphabet == '':
            self.accumulate_alphabet()
        self.generate_password_optional()
        self.recommendations.clear()
        while not self.check_conditions():
            self.generate_password_optional()
            self.recommendations.clear()
        return self.password

    def get_recommendations(self) -> list[str]:
        if len(self.password) < password_parameters.RECOMMENDED_LENGTH:
            self.recommendations.append(f"Длина пароля меньше, чем {password_parameters.RECOMMENDED_LENGTH}.")
        if sum(char in password_parameters.LOWER_CASE for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_LOWER_CASE:
            self.recommendations.append(
                f"Количество букв латинского алфавита в нижнем регистре меньше, чем {password_parameters.RECOMMENDED_NUMBER_OF_LOWER_CASE}.")
        if sum(char in password_parameters.UPPER_CASE for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_UPPER_CASE:
            self.recommendations.append(
                f"Количество букв латинского алфавита в верхнем регистре меньше, чем {password_parameters.RECOMMENDED_NUMBER_OF_UPPER_CASE}.")
        if sum(char in password_parameters.DIGITS for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_DIGITS:
            self.recommendations.append(f"Количество цифр меньше, чем {password_parameters.RECOMMENDED_NUMBER_OF_DIGITS}.")
        if sum(char in password_parameters.SPECIAL_EXTRA for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_SPECIAL:
            self.recommendations.append(f"Количество специальных символов меньше, чем {password_parameters.RECOMMENDED_NUMBER_OF_SPECIAL}.")
        # is_bruteforced = self.check_password_for_rockyou_file(password_parameters.ROCKYOU_PATH)
        # if is_bruteforced == 1:
        #     self.recommendations.append("Пароль находится в базе данных для подбора паролей.")
        # if is_bruteforced == 2:
        #     self.recommendations.append("Часть пароля находится в базе данных для подбора паролей.")
        return self.recommendations

    def password_is_secure(self) -> bool:
        # TODO: add regular expression
        if len(self.password) < password_parameters.RECOMMENDED_LENGTH:
            return False
        if sum(char.islower() for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_LOWER_CASE:
            return False
        if sum(char.isupper() for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_UPPER_CASE:
            return False
        if sum(char.isdigit() for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_DIGITS:
            return False
        if sum(char in password_parameters.SPECIAL_EXTRA for char in self.password) < password_parameters.RECOMMENDED_NUMBER_OF_SPECIAL:
            return False
        if self.math and not any(char in password_parameters.MATH for char in self.password):
            return False
        if self.underscore and not any(char == password_parameters.UNDERSCORE for char in self.password):
            return False
        if self.punctuation and not any(char in password_parameters.PUNCTUATION for char in self.password):
            return False
        if self.special and not any(char in password_parameters.SPECIAL for char in self.password):
            return False
        if self.brackets and not any(char in password_parameters.BRACKETS for char in self.password):
            return False
        # if self.check_password_for_rockyou_file(password_parameters.ROCKYOU_PATH) != 0:
        #     return False
        return True

    def check_conditions(self) -> bool:
        if self.lowercase and not any(char.islower() for char in self.password):
            return False
        if self.uppercase and not any(char.isupper() for char in self.password):
            return False
        if self.digits and not any(char.isdigit() for char in self.password):
            return False
        if self.math and not any(char in password_parameters.MATH for char in self.password):
            return False
        if self.underscore and not any(char == password_parameters.UNDERSCORE for char in self.password):
            return False
        if self.punctuation and not any(char in password_parameters.PUNCTUATION for char in self.password):
            return False
        if self.special and not any(char in password_parameters.SPECIAL for char in self.password):
            return False
        if self.brackets and not any(char in password_parameters.BRACKETS for char in self.password):
            return False
        return True

    def autorun(self) -> Tuple[str, list[str]]:
        self.accumulate_alphabet_by_conditions()
        self.generate_password_by_conditions()
        self.get_recommendations()
        return self.password, self.recommendations

    def check_password_for_rockyou_file(self, file_name: str) -> int:
        with open(file_name, "r", encoding="ansi") as file:
            for line in file:
                if self.password in line:
                    file.close()
                    return 1
                elif len(line) > 3 and line[:-1] in self.password:
                    # len(N), N = 3 due to avoid cases like one letter in password
                    file.close()
                    return 2
        file.close()
        return 0

    def get_password(self) -> str:
        return self.password


# password = GeneratedPassword(uppercase=True)
# password.accumulate_alphabet_by_conditions()
# print(password.alphabet)
# print(f"password is - {password.get_password()}.")
# password.generate_password_by_conditions()
# print(f"password is - {password.get_password()}.")
# print(f"password recommendations: ")
# password.get_recommendations()
# for recommendation in password.recommendations:
#     print(recommendation)

# class PasswordGenerator(object):
#     def __init__(self, password_length=12):
#         self.length: int = password_length
#         self.uppercase: str = ascii_uppercase
#         self.lowercase: str = ascii_lowercase
#         self.digits: str = digits
#         self.special: str = '''\!"#$%&'*+,-./:;<=>?@\^_`|~()[]{}'''
#         self.vocabulary: str = ""
#         self.password: str = ""
#
#     def generate_password(self):
#         if self.vocabulary == "":
#             return "Выберите хотя бы один параметр."
#         for i in range(self.length):
#             self.password += choice(self.vocabulary)
#         return self.password
#
#     def generate_secure_password(self):
#         self.accumulate_vocabulary(True, True, True, True)
#         while self.password_recommendations():
#             self.password = str()
#             for i in range(self.length):
#                 self.password += choice(self.vocabulary)
#         return self.password
#
#     def password_recommendations(self):
#         recommendations = []
#         if not self.password:
#             recommendations.append("Пароль не может быть пустым.")
#             return recommendations
#         if self.length < 12:
#             recommendations.append(f"Длина пароля меньше, чем 12 символов.")
#             return recommendations
#         for what, recommendation in ((self.digits, "Отсутствуют цифры."),
#                                      (self.lowercase, "Отсутствуют строчные буквы."),
#                                      (self.uppercase, "Отсутствуют заглавные буквы."),
#                                      (self.special, "Отсутствуют специальные символы.")):
#             if all(char not in what for char in self.password):
#                 recommendations.append(recommendation)
#         return recommendations
#
#     def accumulate_vocabulary(
#             self,
#             uppercase_use=False,
#             lowercase_use=False,
#             digits_use=False,
#             special_use=False
#     ):
#         if uppercase_use:
#             self.vocabulary += self.uppercase
#         if lowercase_use:
#             self.vocabulary += self.lowercase
#         if digits_use:
#             self.vocabulary += self.digits
#         if special_use:
#             self.vocabulary += self.special
#
#     def get_password(self):
#         return self.password
#
#     def check_patterns(self):
#         ptrn1 = "password"
#         ptrn2 = "ivan"
#         ptrn3 = "sveta"
#         pass
