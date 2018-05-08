<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
@include('partials.user.header')
@yield('head')
<body>
<div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
          @guest
              <a class="navbar-brand" href="{{ url('/') }}">
                  {{ config('app.name', 'Laravel') }}
              </a>
          @else
              <a class="navbar-brand" href="{{ route('home') }}">
                  Home
              </a>
          @endguest
          <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
              <!-- Left Side Of Navbar -->
              <ul class="navbar-nav mr-auto">
              </ul>
              <!-- Right Side Of Navbar -->
              <ul class="navbar-nav ml-auto">
                  <!-- Authentication Links -->
                  @guest
                      <li><a class="nav-link" href="{{ route('login') }}">{{ __('Login') }}</a></li>
                      <li><a class="nav-link" href="{{ route('register') }}">{{ __('Register') }}</a></li>
                  @else
                      <li class="nav-item dropdown">
                          <a id="navbarDropdown" class="nav-link dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" v-pre>
                              My Account <span class="caret"></span>
                          </a>
                          <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                              @if (Auth::user()->profile)
                                  <a class="dropdown-item" href="{{ route('profile.show', ['user_id' => Auth::user()->id,'profile_id' => Auth::user()->profile->id]) }}">My Profile</a>
                              @else
                                  <a class="dropdown-item" href="{{ route('profile.create', ['user_id' => Auth::user()->id]) }}">Create Profile</a>
                              @endif
                              <a class="dropdown-item" href="{{ route('logout') }}"
                                 onclick="event.preventDefault();
                                document.getElementById('logout-form').submit();">
                                  {{ __('Logout') }}
                              </a>
                              <form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
                                  @csrf
                              </form>
                          </div>
                      </li>
                  @endguest
              </ul>
          </div>
      </div>
    </nav>
    <main class="py-4">
        <div class="col-12">
        @include('flash.error')
        @include('flash.messages')
        @include('flash.status')
        </div>
        @yield('content')
    </main>
</div>
@include('partials.user.javascript')
@yield('javascript')
</body>
</html>
