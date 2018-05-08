

<script type="text/javascript" src="{{asset('js/jquery.min.js')}}"></script>
<script type="text/javascript" src="{{asset('js/popper.min.js')}}"></script>
<script type="text/javascript" src="{{asset('js/bootstrap.min.js')}}"></script>
<script type="text/javascript" src="{{asset('js/materialize.min.js')}}"></script>
<script type="text/javascript" src="{{asset('js/jquery-confirm.min.js')}}"></script>
<script type="text/javascript" src="{{asset('js/jquery.dataTables.js')}}"></script>
<script type="text/javascript" src="{{asset('js/off-canvas.js')}}"></script>
<script type="text/javascript" src="{{asset('js/misc.js')}}"></script>
<script>
function sign_out_pro(){
  $.confirm({
      title: 'Alert?',
      icon:'fa fa-unlock',
      theme:'material',
      content: 'Are you sure sign out?',
      autoClose: 'cancel|6000',
      typeAnimated: true,
      animationSpeed: 1000,
      buttons: {
          ok: {
              text: 'Yes',
              action: function () {
                $('#logout-form').submit();
              }
          },
          cancel: {
              text: 'No',
              action: function(){


              }
          }
      }
  });
}
</script>
