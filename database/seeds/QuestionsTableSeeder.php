<?php

use Illuminate\Database\Seeder;

class QuestionsTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $users = App\User::all();
        for ($i = 1; $i <= 16; $i++) {

            $users->each(function ($user) {
                $question = factory(\App\Question::class)->make();
                $question->user()->associate($user);
                $question->save();
            });
        }
    }
}
