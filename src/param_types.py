import click


class RangeParamType(click.ParamType):
    name = 'range'
    TYPE = (int, int)

    def __init__(self, min_start=None, max_end=None):
        self.min_start = min_start
        self.max_end = max_end

    def convert(self, value, param, ctx) -> TYPE:
        try:
            start, end = map(int, value.split(':'))
            if not (start <= end): raise ValueError('Start should be less or equal to end')
            if not (self._is_within_range(start) and self._is_within_range(end)): raise ValueError(f'Given range is not within allowed range: `{self.min_start}:{self.max_end}`')
            return start, end

        except Exception as e:
            self.fail(f'Invalid range format: `{value}`. Expected format: `start:end`. Error: {str(e)}', param, ctx)

    def _is_within_range(self, x: int):
        return self.min_start <= x <= self.max_end


class RatioParamType(click.ParamType):

    name = 'ratio'
    TYPE = float

    def __init__(self, min_ratio=None, max_ratio=None):
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def convert(self, value, param, ctx):
        try:
            den, nom = map(float, value.split(':'))
            ratio = den / nom

            if not self._is_within_range(ratio):
                raise ValueError(f'Given ratio is not within allowed range: `{self.min_ratio:.2f}:{self.max_ratio:.2f}`')

            return ratio

        except Exception as e:
            self.fail(
                f'Invalid format: `{value}`. '
                f'Expected format: `numerator:denominator`. '
                f'Error: {str(e)}',
                param,
                ctx,
            )

    def _is_within_range(self, ratio: TYPE):
        return (
                (not self.min_ratio or ratio >= self.min_ratio) and
                (not self.max_ratio or ratio <= self.max_ratio)
        )
