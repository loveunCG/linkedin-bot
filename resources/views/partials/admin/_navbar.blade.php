<nav class="navbar col-lg-12 col-12 p-0 fixed-top d-flex flex-row">
  <div class="text-center navbar-brand-wrapper d-flex align-items-top justify-content-center">
    <a class="navbar-brand brand-logo" href="#"><img src="{{asset('images/logo.svg')}}" alt="logo"/></a>
    <a class="navbar-brand brand-logo-mini" href="#"><img src="{{asset('images/logo-mini.svg')}}" alt="logo"/></a>
  </div>
  <div class="navbar-menu-wrapper d-flex align-items-center">
    <ul class="navbar-nav navbar-nav-left header-links d-none d-md-flex">
    </ul>
    <ul class="navbar-nav navbar-nav-right">
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" id="notificationDropdown" href="#" data-toggle="dropdown">
          <img class="img-xs rounded-circle" src="{{asset('images/faces-clipart/pic-1.png')}}" alt="">
        </a>
        <div class="dropdown-menu dropdown-menu-right navbar-dropdown preview-list" aria-labelledby="notificationDropdown">
          <div class="dropdown-divider"></div>
          <a class="dropdown-item preview-item">
            <div class="preview-thumbnail">
              <div class="preview-icon bg-warning">
                <i class="icon-user mx-0"></i>
              </div>
            </div>
            <div class="preview-item-content">
              <h6 class="preview-subject font-weight-medium">Settings</h6>
              <p class="font-weight-light small-text">
              </p>
            </div>
          </a>
          <div class="dropdown-divider"></div>
          <a class="dropdown-item preview-item" onclick="sign_out_pro()" >
            <div class="preview-thumbnail">
              <div class="preview-icon bg-info">
                <i class="icon-logout icons mx-0"></i>
              </div>
            </div>
            <div class="preview-item-content">
              <h6 class="preview-subject font-weight-medium" >
                Sign Out
                </h6>
              <p class="font-weight-light small-text">
              </p>
            </div>
          </a>
        </div>
      </li>
    </ul>
    <button class="navbar-toggler navbar-toggler-right d-lg-none align-self-center" type="button" data-toggle="offcanvas">
      <span class="icon-menu"></span>
    </button>
  </div>
</nav>
