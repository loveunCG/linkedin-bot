<?php
/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/
Route::get('/', function () {
    return view('welcome');
});
Auth::routes();
Route::get('/home', 'HomeController@index')->name('home');
Route::get('/user/{user_id}/profile', 'ProfileController@create')->name('profile.create');
Route::get('/user/{user_id}/profile/{profile_id}', 'ProfileController@show')->name('profile.show');
Route::get('/user/{user_id}/profile/{profile_id}/edit', 'ProfileController@edit')->name('profile.edit');
Route::post('/user/{user_id}/profile/', 'ProfileController@store')->name('profile.store');
Route::patch('/user/{user_id}/profile/{profile_id}', 'ProfileController@update')->name('profile.update');
Route::delete('/user/{user_id}/profile/{profile_id}', 'ProfileController@destroy')->name('profile.destroy');
Route::get('/questions/{question_id}/answers/create', 'AnswerController@create')->name('answers.create');
Route::get('/question/{question_id}/answer/{answer_id}', 'AnswerController@show')->name('answers.show');
Route::get('/questions/{question_id}/answers/{answer_id}/edit', 'AnswerController@edit')->name('answers.edit');
Route::post('/questions/{question_id}/answers/', 'AnswerController@store')->name('answers.store');
Route::patch('/questions/{question_id}/answer/{answer_id}', 'AnswerController@update')->name('answers.update');
Route::delete('/questions/{question_id}/answer/{answer_id}', 'AnswerController@destroy')->name('answers.destroy');
Route::resources([
    'questions' => 'QuestionController',
]);

Route::get('/getuserTable', 'AdminController@get_user_table');
Route::get('/getQuestion', 'AdminController@get_question_table');
Route::get('/getAnswer', 'AdminController@get_answer_table');
Route::get('/home', 'HomeController@index')->name('home');

Route::group(['middleware' => ['auth'], 'prefix' => 'admin', 'as' => 'admin.'], function () {
    Route::get('/', 'HomeController@index');
    Route::get('/getuserTable', 'AdminController@get_user_table');
    Route::get('/getQuestion', 'AdminController@get_question_table');
    Route::get('/getAnswer', 'AdminController@get_answer_table');
    Route::get('/question', 'HomeController@question');
    Route::post('/deleteUser', 'AdminController@delete_user');
    Route::post('/deleteQuestion', 'AdminController@remove_question');
    Route::post('/deleteAnswer', 'AdminController@remove_answer');
});
