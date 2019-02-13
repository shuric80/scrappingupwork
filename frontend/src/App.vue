<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>Project</span>
        <span class="font-weight-light">Project</span>
      </v-toolbar-title>
    <v-spacer />
    <v-btn @click="sortDatetime">sort date</v-btn>
    <v-btn v-for="word in words" @click="filterWord(word)">{{word}}</v-btn>
     </v-toolbar>
    <v-layout  align-center justify-center column>
    <v-card v-for="post in posts" @click="post.is_look != post.is_look" :style="stylePost(post.is_look)">
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
        axios.get('http://localhost:5000/api/v1/words').then( o => this.words = o.data).catch(e => console.error(e));
    },
    methods:{
        sortDate: function(){
            //this.posts = this.posts.sort(o => )
        },
        //sortedTms: function(a,b){
        //    if a
       // }
        .
        filter: function(){
            axios.get('http://localhost:5000/api/v1/')

        },
        filterWord: function(w){
            axios.get('http://localhost:5000/api/v1/filter/posts/' + w).then( o => this.posts = o.data).catch(e => console.error(e));
        },
        stylePost: function(state){
            return {
                'max-width': '800px',
                'min-width':'800px',
            }
        }
    },
    data () {
        return {
            posts:[],
            words: []
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
