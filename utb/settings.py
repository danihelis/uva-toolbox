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
    'accept-color':
        True,
    'black-background':
        True,
    'debug':
        False,
    'data-dir':
        '.data',
    'pdf-dir':
        '.pdf',
    'problem-dir':
        'problem',
    'solution-dir':
        'solution',
    'language':
        'c',  # {'c', 'c99', 'cpp', 'python', 'java', 'pascal'}
    'use-volume-in-solution-dir':
        True,

    # Hacks
    'force-cpp-on-ansi-c':
        False,

    # External parameters
    'uhunt':
        'https://uhunt.onlinejudge.org/id/{}',
    'udebug':
        'https://www.udebug.com/UVa/{}',
    'uva-problem':
        'http://uva.onlinejudge.org/external/{}/p{}.pdf',
    'uva-submit':
        'https://uva.onlinejudge.org/index.php',
    'uhunt-api':
        'https://uhunt.onlinejudge.org/api/',

    # Executables
    'pdfviewer':
        'evince {}',
    'browser':
        'firefox {}',
    'terminal':
        'gnome-terminal --working-directory={dir}',
    'editor':
        'gnome-text-editor {}',
    'diff':
        'diff -q {output} {answer} > /dev/null',
    'time':
        '/usr/bin/time -f "%E" -o {time} {run}',
    'c-source':
        '{problem_number}.c',
    'c-exe':
        '{problem_number}',
    'c-compile':
        'gcc -pipe -ansi -pedantic -Wall -O2 {source} -o {exe} -lm -lcrypt',
    'c-run':
        './{exe} < {input} > {output} 2> {error}',
    'c-template':
        """
        /* {problem_number}
         * {problem_name}
         * By {account_name}
         */
        #include <assert.h>
        #include <ctype.h>
        #include <math.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        /* Main function */
        int main() {{
            return EXIT_SUCCESS;
        }}
        """,
    'cpp-source':
        '{problem_number}.cpp',
    'cpp-exe':
        '{problem_number}',
    'cpp-compile':
        'gcc -pipe -std=c++11 -pedantic -Wall -O2 {source} -o {exe} -lm -lcrypt',
    'cpp-run':
        './{exe} < {input} > {output} 2> {error}',
    'cpp-template':
        """
        /* {problem_number}
         * {problem_name}
         * By {account_name}
         */
        #include <cmath>
        #include <cstdlib>
        #include <iostream>

        using namespace std;

        /* Main function */
        int main() {{
            return EXIT_SUCCESS;
        }}
        """,
    'java-source':
        '{problem_number}.java',
    'java-exe':
        'Main.class',
    'java-compile':
        'javac {source} -d {dir} -source 8 -target 8 -Xlint:-options',
    'java-run':
        'java {exe} < {input} > {output} 2> {error}',
    'java-template':
        """
        /* {problem_number}
         * {problem_name}
         * @author {account_name}
         */
        import java.math.*;
        import java.util.*;

        class Main {{

            /* Main method */
            public static void main(String[] args) throws Exception {{
                java.io.PrintStream out = System.out;
                Scanner in = new Scanner(System.in);
            }}
        }}
        """,
    'python-source':
        '{problem_number}.py',
    'python-run':
        'python {source} < {input} > {output} 2> {error}',
    'python-template':
        """
        # {problem_number}
        # {problem_name}
        # By {account_name}
        import math

        # Main code
        ...
        """,
}
