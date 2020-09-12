// Author: Alan Ding

// autocompletion engine for front-end crush search dropdown
let substringMatcher = function(strs) {
    return function findMatches(q, cb) {
        let matches, substrRegex;

        // an array that will be populated with substring matches
        matches = [];

        // regex used to determine if a string contains the substring `q`
        substrRegex = new RegExp(q, 'i');

        // iterate through the pool of strings and for any string that
        // contains the substring `q`, add it to the `matches` array
        $.each(strs, function(i, str) {
          if (substrRegex.test(str)) {
            matches.push({value: str});
          }
        });

        cb(matches);
    };
};

$(document).ready(function() {
    $.get(
        '/studentInfo', {},
        function(result) {
            let students = result.data;

            $('#crushSelector').typeahead({
                hint: true,
                highlight: true,
                minLength: 3
            },
            {
                source: substringMatcher(students)
            }).blur(function () { // ensure user picks one of the suggestions
                if (students.indexOf($(this).val()) === -1) {
                    $('#crushSelector').val('');
                }
            });
        }
    );
});