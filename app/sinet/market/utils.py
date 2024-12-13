from abc import abstractmethod
import re


class Spider:
    @abstractmethod
    def run(self): ...

    def to_float(self, value):
        if not value:
            return value

        if isinstance(value, (int, float)):
            return round(float(value), 2)

        try:
            number = round(
                float(str(value).replace(" ", "").replace(",", ".").replace("%", "")), 2
            )
        except Exception:
            return value

        return "{0:.2f}".format(number)

    def to_float_old(self, value):

        if len(value) == 0:
            return value
        try:
            # replace string to numbers
            value = str(value).replace(" ", "").replace("%", "")
            value = re.findall(r"-?\s*\d+(?:\.\d+)?", str(value))
            # value = str(value).replace("K", "000").replace("M", "000000").replace("B", "000000000")
            # value = str(value).replace(" ", "").replace(',', '.').replace('%', '')

            number = round(float(value, 2))

        except Exception:
            return value
        return "{0:.2f}".format(number)
