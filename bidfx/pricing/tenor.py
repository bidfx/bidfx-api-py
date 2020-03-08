__all__ = ["Tenor"]

from bidfx.exceptions import PricingError


class Tenor:
    """
    Tenor values for defining the settlement period in a `Subject` for FX futures and swaps.
    """

    BROKEN_DATE = "BD"
    """Broken data tenor implied that an explicit settlement date is provided. 
    """
    TODAY = "TOD"
    """Today or same day settlement. 
    """
    TOMORROW = "TOM"
    """Tomorrow or next day settlement. Next good business day after today.
    """
    SPOT = "Spot"
    """Spot date settlement. Spot is T+1 or T+2 depending of the currency pair.
    """
    SPOT_NEXT = "S/N"
    """Spot/next settlement. The next good business day after spot. 
    """

    IN_1_WEEK = "1W"
    """Settlement in one week. 
    """
    IN_2_WEEKS = "2W"
    """Settlement in two weeks. 
    """
    IN_3_WEEKS = "3W"
    """Settlement in three weeks. 
    """

    IN_1_MONTH = "1M"
    """Settlement in one month. 
    """
    IN_2_MONTHS = "2M"
    """Settlement in two months. 
    """
    IN_3_MONTHS = "3M"
    """Settlement in three months. 
    """
    IN_4_MONTHS = "4M"
    """Settlement in four months. 
    """
    IN_5_MONTHS = "5M"
    """Settlement in five months. 
    """
    IN_6_MONTHS = "6M"
    """Settlement in six months. 
    """
    IN_7_MONTHS = "7M"
    """Settlement in seven months. 
    """
    IN_8_MONTHS = "8M"
    """Settlement in eight months. 
    """
    IN_9_MONTHS = "9M"
    """Settlement in nine months. 
    """
    IN_10_MONTHS = "10M"
    """Settlement in ten months. 
    """
    IN_11_MONTHS = "11M"
    """Settlement in eleven months. 
    """
    IN_18_MONTHS = "18M"
    """Settlement in eighteen months. 
    """
    IN_30_MONTHS = "30M"
    """Settlement in thirty months. 
    """

    IN_1_YEAR = "1Y"
    """Settlement in one year. 
    """
    IN_2_YEARS = "2Y"
    """Settlement in two years. 
    """
    IN_3_YEARS = "3Y"
    """Settlement in three years. 
    """
    IN_4_YEARS = "4Y"
    """Settlement in four years. 
    """
    IN_5_YEARS = "5Y"
    """Settlement in five years. 
    """

    IMM_MARCH = "IMMH"
    """Settlement coinciding with the IMM cash futures contract for March. 
    """
    IMM_JUNE = "IMMM"
    """Settlement coinciding with the IMM cash futures contract for June. 
    """
    IMM_SEPTEMBER = "IMMU"
    """Settlement coinciding with the IMM cash futures contract for September. 
    """
    IMM_DECEMBER = "IMMZ"
    """Settlement coinciding with the IMM cash futures contract for December. 
    """

    @classmethod
    def of_week(cls, week: int):
        """
        Gets the weekly tenor of the given number of weeks.
        :param week: number of weeks
        :return: the tenor value
        """
        if week == 1:
            return cls.IN_1_WEEK
        elif week == 2:
            return cls.IN_2_WEEKS
        elif week == 3:
            return cls.IN_3_WEEKS
        else:
            raise PricingError(f"invalid weekly tenor of {week} weeks")

    @classmethod
    def of_month(cls, month: int):
        """
        Gets the monthly tenor of the given number of months.
        :param month: number of months
        :return: the tenor value
        """
        if month == 1:
            return cls.IN_1_MONTH
        elif month == 2:
            return cls.IN_2_MONTHS
        elif month == 3:
            return cls.IN_3_MONTHS
        elif month == 4:
            return cls.IN_4_MONTHS
        elif month == 5:
            return cls.IN_5_MONTHS
        elif month == 6:
            return cls.IN_6_MONTHS
        elif month == 7:
            return cls.IN_7_MONTHS
        elif month == 8:
            return cls.IN_8_MONTHS
        elif month == 9:
            return cls.IN_9_MONTHS
        elif month == 10:
            return cls.IN_10_MONTHS
        elif month == 11:
            return cls.IN_11_MONTHS
        elif month == 18:
            return cls.IN_18_MONTHS
        elif month == 30:
            return cls.IN_30_MONTHS
        else:
            raise PricingError(f"invalid monthly tenor of {month} months")

    @classmethod
    def of_year(cls, year: int):
        """
        Gets the yearly tenor of the given number of years.
        :param year: number of months
        :return: the tenor value
        """
        if year == 1:
            return cls.IN_1_YEAR
        elif year == 2:
            return cls.IN_2_YEARS
        elif year == 3:
            return cls.IN_3_YEARS
        elif year == 4:
            return cls.IN_4_YEARS
        elif year == 5:
            return cls.IN_5_YEARS
        else:
            raise PricingError(f"invalid yearly tenor of {year} years")

    @classmethod
    def of_imm_month(cls, month):
        """
        Gets the IMM monthly contract tenor of the given month.
        :param month: months number in year 1..12
        :return: the tenor value
        """
        if month == 3:
            return cls.IMM_MARCH
        elif month == 6:
            return cls.IMM_JUNE
        elif month == 9:
            return cls.IMM_SEPTEMBER
        elif month == 12:
            return cls.IMM_DECEMBER
        else:
            raise PricingError(f"invalid IMM monthly tenor for month {month}")
