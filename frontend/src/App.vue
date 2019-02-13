<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>Project</span>
        <span class="font-weight-light">Project</span>
      </v-toolbar-title>
    <v-spacer />
    <v-btn @click="filter">filter</v-btn>
    </v-toolbar>
    <v-layout  align-center justify-center column>
    <v-card v-for="post in posts" :href="post.url" style="max-width:800px">
    <v-card-title class="title">{{ post.title }}</v-card-title>
    <v-card-text><p><span class="type">{{ post.ptype.split('.')[1]}}</span><span class="duration"> {{ post.duration}}</span><span class="posted_time">{{ post.posted_time}}</span></p>
                                   <div class="description">{{post.description}}</div>
    <p>
      <span class="verifyed" v-if="post.payment">Payment verified</span>
      <span class="proposal">{{post.proposal}}</span>
      <span class="spent">{{post.spent}}</span>
      <span class="location">{{post.location}}</span>
    </p>
     </v-card-text>
     </v-card>
    </v-layout>
  </v-app>
</template>

<script>

import axios from 'axios'

export default {
    name: 'App',
    created: function(){
        axios.get('http://localhost:5000/api/v1/posts').then( o => this.posts = o.data).catch(e => console.error(e));
    },
    data () {
        return {
            posts:[]
            //
        }
    }
}
</script>
    <style>
    body {
        font-size: 100;
    }
    .description {
        padding-bottom: 20px;
    }
    .title {
    }
    .posted_time {
        background-color:teal ;
        color: white;
        margin: 10px;
        padding: 4px;
    }
    .duration {
        background-color: teal;
        color: white;
        margin: 10px;
        padding: 4px;
    }

    .type {
        background-color: teal;
        color: white;
        margin: 10px;
        padding: 4px;
    }
    .title:hover {
        background-color: #AAA;
        color: white;
    }

    .verifyed {
        margin: 10px;
        padding: 4px;
        background-color: teal;
        color:white;
    }
    .proposal {
        margin: 10px;
        padding: 4px;
        background-color: teal;
        color: white;
    }
    .spent {
        margin: 10px;
        padding: 4px;
        background-color: teal;
        color: white;
    }
    .location {
        margin: 10px;
        padding: 4px;
        background-color: teal;
        color: white;
    }
    </style>
