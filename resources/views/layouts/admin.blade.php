<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
@include('partials.admin.header')
@yield('head')
<body>
  <div class="container-scroller">
    @include('partials.admin._navbar')
    <div class="container-fluid page-body-wrapper">
      @include('partials.admin._sidebar')
      <div class="main-panel">
        <div class="content-wrapper">
          @yield('content')
        </div>
        @include('partials.admin._footer')
      </div>
    </div>
  </div>
@include('partials.admin.javascript')
@yield('javascript')
</body>
</html>
