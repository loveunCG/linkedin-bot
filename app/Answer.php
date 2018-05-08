<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

/**
 * App\Answer
 *
 * @property int $id
 * @property int $user_id
 * @property int $question_id
 * @property string $body
 * @property \Carbon\Carbon|null $created_at
 * @property \Carbon\Carbon|null $updated_at
 * @property-read \App\Question $question
 * @property-read \App\User $user
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Answer whereBody($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Answer whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Answer whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Answer whereQuestionId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Answer whereUpdatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Answer whereUserId($value)
 * @mixin \Eloquent
 */
class Answer extends Model
{
    protected $fillable = ['body'];

    public function user()
    {
        return $this->belongsTo('App\User');
    }
    public function question()
    {
        return $this->belongsTo('App\Question');
    }
}
