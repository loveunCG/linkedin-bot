<head>
  <!-- Required meta tags -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Admin {{ config('app.name', 'Laravel') }}</title>
  <!-- plugins:css -->
  <link href="{{ asset('css/style.css') }}" rel="stylesheet">
  <link href="{{ asset('css/materialdesignicons.min.css') }}" rel="stylesheet">
  <link href="{{ asset('css/simple-line-icons.css') }}" rel="stylesheet">
  <link href="{{ asset('css/datatables.min.css') }}" rel="stylesheet">
  <link href="{{ asset('css/materialize.min.css') }}" rel="stylesheet">
  <link href="{{ asset('css/jquery-confirm.min.css') }}" rel="stylesheet">
</head>
<form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
    @csrf
</form>
