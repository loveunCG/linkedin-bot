<nav class="sidebar sidebar-offcanvas" id="sidebar">
  <ul class="nav">
    <li class="nav-item nav-profile">
      <div class="nav-link">
        <div class="profile-image"> <img src="{{asset('images/faces-clipart/pic-1.png')}}" alt="image"/> <span class="online-status online"></span> </div>
        <div class="profile-name">
          <p class="name">{{$user->email}}</p>
          <p class="designation">{{$user->type}}</p>
        </div>
      </div>
    </li>
    <li class="nav-item"><a class="nav-link" href="{{url('admin')}}"><img class="menu-icon" src="{{asset('images/menu_icons/01.png')}}" alt="menu icon"><span class="menu-title">User Manage</span></a></li>
    <li class="nav-item"><a class="nav-link" href="{{url('admin/question')}}"><img class="menu-icon" src="{{asset('images/menu_icons/02.png')}}" alt="menu icon"><span class="menu-title">Question Manage</span></a></li>
  </ul>
</nav>
