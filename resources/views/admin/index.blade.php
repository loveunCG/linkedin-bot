@extends('layouts.admin')
@section('content')

<div class="row">
  <div class="col-lg-12 stretch-card">
    <div class="card">
      <div class="card-body">
        <h4 class="card-title">User List</h4>
        <p class="card-description">
            <!-- <a class="btn-floating btn-large waves-effect waves-light red modal-trigger"  href="#addUserModal"><i class="mdi mdi-plus"></i></a> -->
        </p>
        <table class="table table-bordered" id="user_table_field">
        </table>
      </div>
    </div>
  </div>
</div>
<div id="questionModal" class="modal modal-fixed-footer">
  <div class="card">
      <div class="card-body">
        <h4 class="card-title">Questions List</h4>
      <table class="table table-bordered" id="question_table_flied">
      </table>
    </div>
  </div>
  <div class="modal-footer">
    <a class="btn waves-effect waves-light red" onclick="questionModal()">close</a>
  </div>
</div>
<form id="delete_user_form">
    <input type="hidden" name="user_id" id="user_delete_id"/>
      @csrf
</form>
@endsection
@section('javascript')
<script type="text/javascript">
    var userTable, questioinTable;
    var ajax_user_table_url = '{{url('/admin/getuserTable')}}';
    var ajax_question_table_url = '{{url('/admin/getQuestion')}}';
    $(function(){
        $('.modal').modal();
        userTable = $('#user_table_field').DataTable( {
            "ajax": ajax_user_table_url,
            "order": [[ 0, "asc" ]],
            "bLengthChange": false,
            "bFilter": true,
            "columns": [
                { "data": "no" },
                { "data": "name" },
                { "data": "email" },
                { "data": "type" },
                { "data": "join_time" },
                { "data": "action" },
            ],
            "searching": false,
            "columnDefs": [
                {  "title": "No", "targets": 0 },
                {  "title": "Name",  "targets": 1 },
                {  "title": "Email","targets": 2 },
                {  "title": "Type", "targets": 3 },
                {  "title": "Join Time", "targets": 4 },
                {  "title": "Action",  "targets": 5 },
                {"className": "dt-center", "targets": "_all"}
             ],
            "bAutoWidth": false
        });
        questioinTable = $('#question_table_flied').DataTable( {
            "ajax": ajax_question_table_url,
            "order": [[ 0, "asc" ]],
            "bLengthChange": false,
            "bFilter": true,
            "columns": [
                { "data": "no" },
                { "data": "question" },
                { "data": "name" },
                { "data": "create_at" },
                { "data": "answerofnum" },
            ],
            "searching": false,
            "columnDefs": [
                {  "title": "No", "targets": 0 },
                {  "title": "Question",  "targets": 1 },
                {  "title": "User Name","targets": 2 },
                {  "title": "Created At", "targets": 3 },
                {  "title": "Answer Number", "targets": 4 },
                {"className": "dt-center", "targets": "_all"}
             ],
            "bAutoWidth": false
        });
    });


    function questionModal(){
      $('#questionModal').modal('close');
    }
    function viewQuestion(param){
      var ajaxurl = ajax_question_table_url + '/?user_id=' + param;
			questioinTable.ajax.url(ajaxurl).load();
      $('#questionModal').modal('open');
    }

    function deleteUser(param) {
      $('#user_delete_id').val(param)
      var formData = $('#delete_user_form').serialize()
      let settings = {
          "url": "{{url('/admin/deleteUser')}}",
          "method": "POST",
          "data": formData
      };
      console.log(formData);
      $.confirm({
          title: 'Alert',
          content: ' Are you sure you want to delete this account?',
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
                                              userTable.ajax.reload();
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
