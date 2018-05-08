@extends('layouts.user')

@section('content')
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">My Profile</div>
                    <div class="card-body">
                        @if($edit === FALSE)
                            {!! Form::model($profile, ['route' => ['profile.store', Auth::user()->id], 'method' => 'post']) !!}
                        @else()
                            {!! Form::model($profile, ['route' => ['profile.update', Auth::user()->id, $profile->id], 'method' => 'patch']) !!}
                        @endif
                        <div class="form-group">
                            {!! Form::label('fname', 'First Name') !!}
                            {!! Form::text('fname', $profile->fname, ['class' => 'form-control','required' => 'required']) !!}
                        </div>
                        <div class="form-group">
                            {!! Form::label('lname', 'Last Name') !!}
                            {!! Form::text('lname', $profile->lname, ['class' => 'form-control','required' => 'required']) !!}
                        </div>
                        <div class="form-group">
                            {!! Form::label('body', 'Body') !!}
                            {!! Form::text('body', $profile->body, ['class' => 'form-control','required' => 'required']) !!}
                        </div>
                        <button class="btn btn-success float-right" value="submit" type="submit" id="submit">Save
                        </button>
                        {!! Form::close() !!}
                    </div>

                </div>
            </div>
        </div>
    </div>
@endsection