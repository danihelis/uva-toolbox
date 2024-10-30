# utb: UVa Online Judge toolbox
# Copyright (C) 2024  Daniel Donadon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def to_roman(value):
    symbols = ['I', 'V', 'X', 'L', 'C', 'D', 'M']
    if value <= 0 or value >= 4000:
        return None
    order = 0
    roman = ''
    while value > 0:
        number = value % 10
        high = order + 1
        result = ''
        if number >= 5:
            result = symbols[high]
            high += 1
            number -= 5
        if number == 4:
            result = symbols[order] + symbols[high]
        else:
            for i in range(number):
                result += symbols[order]
        roman = result + roman
        order += 2
        value = value // 10
    return roman
