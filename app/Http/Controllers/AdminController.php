<?php

namespace App\Http\Controllers;

use App\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use App\Question;
use App\Answer;

class AdminController extends Controller
{
    public function get_user_table(Request $request)
    {
        $user_list['data'] = [];

        try {
            $users = User::where('type', 'user')->get();
            $i = 1;
            if (count($users) > 0) {
                foreach ($users as $user) {
                    $action = '<button class="btn-floating btn waves-effect waves-light blue" onclick="viewQuestion('.$user->id.')" type="button"><i class="mdi mdi-eye"></i></button>';
                    $action .= '<button class="btn-floating btn waves-effect waves-light red" onclick="deleteUser('.$user->id.')" type="button"><i class="mdi mdi-delete"></i></button>';
                    $user_list['data'][] = [
                'no' => $i++,
                'name' => isset($user->profile) ? $user->profile->fname.' '.$user->profile->lname : ' ',
                'email' => $user->email,
                'type' => $user->type,
                'join_time' => $user->created_at->format('Y-m-d h:i:s'),
                'action' => $action,
              ];
                }
            }
        } catch (\Exception $e) {
            $user_list['data'] = [];
        }

        return response()->json($user_list);
    }

    public function delete_user(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'user_id' => 'required',
        ]);
        if ($validator->fails()) {
            return response()->json(['message' => 'Submit Error!', 'data' => $validator->errors(), 'response_code' => 0], 200);
        }
        try {
            $user = User::findOrFail($request->user_id);
            $user->delete();

            return response()->json(['message' => 'User has been deleted!', 'data' => [], 'response_code' => 1], 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Server Error!', 'data' => $e, 'response_code' => 0], 200);
        }
    }

    public function get_question_table(Request $request)
    {
        $question_list['data'] = [];
        try {
            $i = 1;
            if ($request->user_id) {
                $questions = Question::where('user_id', $request->user_id)->get();
            } else {
                $questions = Question::all();
            }
            foreach ($questions as $key => $question) {
                $action = '<button class="btn-floating btn waves-effect waves-light blue" onclick="viewAnswer('.$question->id.')" type="button"><i class="mdi mdi-eye"></i></button>';
                $action .= '<button class="btn-floating btn waves-effect waves-light red" onclick="deleteQuestion('.$question->id.')" type="button"><i class="mdi mdi-delete"></i></button>';
                $body = $question->body;
                $question_list['data'][] = [
              'no' => $i++,
              'question' => $body,
              'email' => $question->user->email,
              'name' => isset($question->user->profile) ? $question->user->profile->fname.' '.$question->user->profile->lname : $question->user->email,
              'create_at' => $question->created_at->format('Y-m-d h:i:s'),
              'answerofnum' => count($question->answers),
              'action' => $action,
            ];
            }

            return response()->json($question_list);
        } catch (\Exception $e) {
            $question_list['data'] = [];

            return response()->json($question_list);
        }
    }

    public function remove_question(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'question_id' => 'required',
        ]);
        if ($validator->fails()) {
            return response()->json(['message' => 'Submit Error!', 'data' => $validator->errors(), 'response_code' => 0], 200);
        }
        try {
            $user = Question::findOrFail($request->question_id);
            $user->delete();

            return response()->json(['message' => 'Question has been deleted!', 'data' => [], 'response_code' => 1], 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Server Error!', 'data' => [], 'response_code' => 0], 200);
        }
    }

    public function get_answer_table(Request $request)
    {
        $answer_list['data'] = [];

        try {
            $i = 1;
            if ($request->question_id) {
                $answers = Answer::where('question_id', $request->question_id)->get();
            } else {
                $answers = Answer::all();
            }
            foreach ($answers as $key => $answer) {
                $action = '<button class="btn-floating btn waves-effect waves-light red" onclick="deleteAnswer('.$answer->id.')" type="button"><i class="mdi mdi-delete"></i></button>';
                $body = $answer->body;
                $answer_list['data'][] = [
              'no' => $i++,
              'question' => $answer->question->body,
              'answer' => $body,
              'name' => isset($answer->user->profile) ? $answer->user->profile->fname.' '.$answer->user->profile->lname : $answer->user->email,
              'create_at' => $answer->created_at->format('Y-m-d h:i:s'),
              'action' => $action,
            ];
            }

            return response()->json($answer_list);
        } catch (\Exception $e) {
            $answer_list['data'] = [];

            return response()->json($answer_list);
        }
    }

    public function remove_answer(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'answer_id' => 'required',
        ]);
        if ($validator->fails()) {
            return response()->json(['message' => 'Submit Error!', 'data' => $validator->errors(), 'response_code' => 0], 200);
        }
        try {
            $user = Answer::findOrFail($request->answer_id);
            $user->delete();

            return response()->json(['message' => 'Question has been deleted!', 'data' => [], 'response_code' => 1], 200);
        } catch (\Exception $e) {
            return response()->json(['message' => 'Server Errors!', 'data' => [], 'response_code' => 0], 200);
        }
    }
}
