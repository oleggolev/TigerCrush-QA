// Author: Alan Ding

// dynamically populate crush list
$.ajax({
    method: 'GET',
    url: '/getCrushes?netid=' + $('#netidStore').attr('value'), // + netid
    success: function(result) {
        let students = result.data;
        if (students.length === 0) {
            $('#crushList').append('<p class="card-text pt-3">You have not added any crushes yet. Get started above!</p>');
        } else {
            $('#crushList').append('<div class="table-responsive pt-3">\n' +
                '<table class="table table-striped table-borderless border">\n' +
                '<tbody>\n'
            );

            for (let name of students) {
                $('#crushList tbody').append('<tr class="text-center">\n' +
                    '<td class="">' + name + '</td>\n' +
                    '</tr>\n'
                );
            }

            $('#crushList').append('</tbody>\n' +
                '</table>\n' +
                '</div>'
            );
        }
    }
});

// dynamically populate match list
$.ajax({
    method: 'GET',
    url: '/getMatches?netid=' + $('#netidStore').attr('value'), // + netid
    success: function(result) {
        let students = result.data;
        if (students.length === 0) {
            $('#matchList').append('<p class="card-text pb-3">You have not been matched to one of your crushes yet :(</p>');
        } else {
            $('#matchList').append('<p class="card-text text-primary">Congratulations! You\'ve been matched! It\'s up to you to take things from here.</p>');
            $('#matchList').append('<div class="table-responsive">\n' +
                '<table class="table table-striped table-borderless border">\n' +
                '<tbody>\n'
            );

            for (let name of students) {
                $('#matchList tbody').append('<tr class="text-center">\n' +
                    '<td class="">' + name + '</td>\n' +
                    '</tr>\n'
                );
            }

            $('#matchList').append('</tbody>\n' +
                '</table>\n' +
                '</div>'
            );
        }
    }
});