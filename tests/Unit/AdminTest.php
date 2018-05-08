<?php

namespace Tests\Unit;

use Tests\TestCase;

class AdminTest extends TestCase
{
    /**
     * A basic test example.
     */
    public function testExample()
    {
        $this->assertTrue(true);
    }

    public function testGetUserTable()
    {
        $response = $this->withHeaders([
           'X-Header' => 'Value',
       ])->json('GET', 'getuserTable', ['name' => 'Sally']);
        $response->assertStatus(200)
                 ->assertJson(['data' => true]);
    }

    public function testGetQuestionTable()
    {
        $response = $this->withHeaders([
               'X-Header' => 'Value',
           ])->json('GET', '/getQuestion', ['name' => 'Sally']);
        $response->assertStatus(200)->assertJson(['data' => true]);
    }

    public function testAnswerTable()
    {
        $response = $this->withHeaders([
                   'X-Header' => 'Value',
               ])->json('GET', '/getAnswer', ['name' => 'Sally']);
        $response->assertStatus(200)->assertJson(['data' => true]);
    }
}
