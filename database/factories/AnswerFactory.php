<?php

use Faker\Generator as Faker;

$factory->define(App\Answer::class, function (Faker $faker) {
    return [
        //
        'body' => $faker->paragraph($nbSentences = 3, $variableNbSentences = true),
    ];
});
