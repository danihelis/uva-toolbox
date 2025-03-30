# utb: UVa Online Judge toolbox
# Copyright (C) 2024-2025  Daniel Donadon
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

DEFAULT_SETTINGS = {
    # General parameters
    'accept-color': True,
    'debug': False,
    'data-dir': '.data',
    'pdf-dir': '.pdf',
    'problem-dir': 'problem',
    'solution-dir': 'solution',
    'copy-solution': True,
    'erase-after-accepted': True,
    'language': 'c',

    # External parameters
    'number-books': 4,
    'uva-problem': 'http://uva.onlinejudge.org/external/{}/p{}.pdf',
    'uva-submit': 'https://uva.onlinejudge.org/index.php',
    'uhunt-api': 'https://uhunt.onlinejudge.org/api/',
    'uhunt-page': 'https://uhunt.onlinejudge.org/id/{}',
    'udebug': 'https://www.udebug.com/UVa/{}',

    # Executables
    'pdfviewer': 'evince {}',
    'editor': 'gnome-text-editor {}',
    'diff': 'diff -q {first} {second} > /dev/null',
    'time': '/usr/bin/time -f "%E" -o {time} {run}',
    'c-compile': 'gcc -pipe -ansi -pedantic -Wall -O2 {source} -o {exe} -lm -lcrypt',
    'c-run': '{exe} < {input} > {output} 2> {error}',
    'cpp-compile': 'gcc -pipe -std=c++11 -pedantic -Wall -O2 {source} -o {exe} -lm -lcrypt',
    'cpp-run': '{exe} < {input} > {output} 2> {error}',

    # Solution templates
    'c-source': '{problem_number}.c',
    'c-template': """
        /* {problem_number}
         * {problem_name}
         * By {account_name}
         */
        #include <stdlib.h>
        #include <stdio.h>
        #include <string.h>
        #include <ctype.h>
        #include <assert.h>
        #include <math.h>

        /* Main function */
        int main() {{
            return EXIT_SUCCESS;
        }}
        """,
    'cpp-source': '{problem_number}.cpp',
    'cpp-template': """
        /* {problem_number}
         * {problem_name}
         * By {account_name}
         */
        #include <cstdlib>
        #include <cmath>
        #include <iostream>

        using namespace std;

        /* Main function */
        int main() {{
            return EXIT_SUCCESS;
        }}
        """,
}
