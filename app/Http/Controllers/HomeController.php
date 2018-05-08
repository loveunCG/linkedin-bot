<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Gate;
use App\User;

class HomeController extends Controller
{
    /**
     * Create a new controller instance.
     */
    public function __construct()
    {
        $this->middleware('auth');
    }

    /**
     * Show the application dashboard.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        $user = Auth::user();

        if (Gate::allows('is-admin', $user)) {
            $users = User::all();

            return view('admin.index', compact('user', 'users'));
        } else {
            $questions = $user->questions()->paginate(6);

            return view('home')->with('questions', $questions);
        }
    }

    public function question()
    {
        $user = Auth::user();
        if (Gate::allows('is-admin', $user)) {
            $users = User::all();

            return view('admin.question', compact('user', 'users'));
        } else {
            $questions = $user->questions()->paginate(6);

            return view('home')->with('questions', $questions);
        }
    }
}
