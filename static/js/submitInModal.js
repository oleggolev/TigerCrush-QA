// Author: Alan Ding

function isInputEmpty() {
    return $('#crushSelector').val() === '';
}

$('#addCrushButton').click(function() {
    if (isInputEmpty()) {
        $('#crushSelector').addClass('is-invalid');
    }
    else {
        $('#confirmationMsg').html('Are you sure you want to add ' +
            $('#crushSelector').val() + ' as a crush?');
        $('#confirmModal').modal('show');
    }
});

$('#submitButton').click(function() {
    if (!isInputEmpty())
        $('#addCrushForm').submit();
});