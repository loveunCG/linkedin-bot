@extends('layouts.admin')
@section('content')

<div class="row">
  <div class="col-lg-12 stretch-card">
    <div class="card">
      <div class="card-body">
        <h4 class="card-title">Question List</h4>
        <p class="card-description">
            <!-- <a class="btn-floating btn-large waves-effect waves-light red modal-trigger"  href="#addUserModal"><i class="mdi mdi-plus"></i></a> -->
        </p>
        <table class="table responsive-table highlight" id="question_table_field">
        </table>
      </div>
    </div>
  </div>
</div>
<div id="answerModal" class="modal modal-fixed-footer">
  <div class="card">
      <div class="card-body">
        <h4 class="card-title">Answer List</h4>
      <table class="table responsive-table highlight" id="answer_table_field">
      </table>
    </div>
  </div>
  <div class="modal-footer">
    <a class="btn waves-effect waves-light red" onclick="answerModal()">close</a>
  </div>
</div>
<form id="delete_question_form">
    <input type="hidden" name="question_id" id="question_delete_id"/>
      @csrf
</form>

<form id="delete_answer_form">
    <input type="hidden" name="answer_id" id="answer_delete_id"/>
      @csrf
</form>

<input type="hidden" id = "tmp_question_id"/>
@endsection
@section('javascript')
<script type="text/javascript">
    var questionTable, answerTable;
    var ajax_answer_table_url = '{{url('/admin/getAnswer')}}';
    var ajax_question_table_url = '{{url('/admin/getQuestion')}}';
    $(function(){
        $('.modal').modal();
        questionTable = $('#question_table_field').DataTable( {
            "ajax": ajax_question_table_url,
            "order": [[ 0, "asc" ]],
            "bLengthChange": false,
            "bFilter": true,
            "columns": [
                { "data": "no" },
                { "data": "name" },
                { "data": "question" },
                { "data": "create_at" },
                { "data": "answerofnum" },
                { "data": "action" },
            ],
            "searching": false,
            "columnDefs": [
                {  "title": "No", "targets": 0 },
                {  "title": "Name",  "targets": 1 },
                {  "title": "Question", "targets": 2 },
                {  "title": "Created At", "targets": 3 },
                {  "title": "Answers",  "targets": 4 },
                {  "title": "Action",  "targets": 5 },
                {"className": "dt-center", "targets": "_all"}
             ],
            "bAutoWidth": false
        });
        answerTable = $('#answer_table_field').DataTable( {
            "ajax": ajax_answer_table_url,
            "order": [[ 0, "asc" ]],
            "bLengthChange": false,
            "bFilter": true,
            "columns": [
                { "data": "no" },
                { "data": "question" },
                { "data": "name" },
                { "data": "answer" },
                { "data": "create_at" },
                { "data": "action" },
            ],
            "searching": false,
            "columnDefs": [
                {  "title": "No", "targets": 0 },
                {  "title": "Question",  "targets": 1 },
                {  "title": "User Name","targets": 2 },
                {  "title": "Answer", "targets": 3 },
                {  "title": "Create At", "targets": 4 },
                {  "title": "action", "targets": 5 },
                {"className": "dt-center", "targets": "_all"}
             ],
            "bAutoWidth": false
        });
    });

    function deleteAnswer(param){
      $('#answer_delete_id').val(param)
      var formData = $('#delete_answer_form').serialize()
      let settings = {
          "url": "{{url('/admin/deleteAnswer')}}",
          "method": "POST",
          "data": formData
      };
      $.confirm({
          title: 'Alert',
          content: ' Are you sure you want to delete this Answer?',
          icon: 'fa fa-warning',
          theme: 'material',
          autoClose: 'chancel|5000',
          animation: 'zoom',
          closeAnimation: 'scale',
          draggable: true,
          buttons: {
              confirm: {
                  text: 'Yes',
                  keys: ['shift', 'alt'],
                  action: function () {
                      $.ajax(settings).done(function (response) {
                          console.log(response)
                          $.alert({
                              title: 'Alert!',
                              content: response.message,
                              columnClass: 'small',
                              theme: 'material',
                              buttons: {
                                  ok: {
                                      text: 'Ok',
                                      btnClass: 'btn-yellow',
                                      action: function () {
                                          if(response.response_code){
                                              questionTable.ajax.reload();
                                              var ajaxurl = ajax_answer_table_url + '/?question_id=' +   $('#tmp_question_id').val();
                                        			answerTable.ajax.url(ajaxurl).load();
                                              $(this).remove();
                                          }else{

                                          }
                                      }
                                  }
                              }
                          });
                      })
                      .fail(function(err) {
                          console.log( err );
                      });
                  }
              },
              chancel: {
                  text: 'No',
                  action: function () {
                      $(this).remove();
                  }

              }
          }
      });
    }


    function answerModal(){
      $('#answerModal').modal('close');
    }
    function viewAnswer(param){
      $('#tmp_question_id').val(param);
      var ajaxurl = ajax_answer_table_url + '/?question_id=' + param;
			answerTable.ajax.url(ajaxurl).load();
      $('#answerModal').modal('open');
    }

    function deleteQuestion(param) {
      $('#question_delete_id').val(param)
      var formData = $('#delete_question_form').serialize()
      let settings = {
          "url": "{{url('/admin/deleteQuestion')}}",
          "method": "POST",
          "data": formData
      };
      $.confirm({
          title: 'Alert',
          content: ' Are you sure you want to delete this Question?',
          icon: 'fa fa-warning',
          theme: 'material',
          autoClose: 'chancel|5000',
          animation: 'zoom',
          closeAnimation: 'scale',
          draggable: true,
          buttons: {
              confirm: {
                  text: 'Yes',
                  keys: ['shift', 'alt'],
                  action: function () {
                      $.ajax(settings).done(function (response) {
                          console.log(response)
                          $.alert({
                              title: 'Alert!',
                              content: response.message,
                              columnClass: 'small',
                              theme: 'material',
                              buttons: {
                                  ok: {
                                      text: 'Ok',
                                      btnClass: 'btn-yellow',
                                      action: function () {
                                          if(response.response_code){
                                              questionTable.ajax.reload();
                                              $(this).remove();
                                          }else{

                                          }
                                      }
                                  }
                              }
                          });
                      })
                      .fail(function(err) {
                          console.log( err );
                      });
                  }
              },
              chancel: {
                  text: 'No',
                  action: function () {
                      $(this).remove();
                  }

              }
          }
      });
    }
</script>
@endsection
