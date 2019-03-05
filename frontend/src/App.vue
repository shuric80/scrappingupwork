<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>Project</span>
        <span class="font-weight-light">Project</span>
      </v-toolbar-title>
    <v-spacer />
    </v-toolbar>
    <v-navigation-drawer fixed height="100%" right>
    <v-btn @click="sortDateTime" flat color="green">Sort time</v-btn>
    <v-list >
    <v-list-tile v-for="word in words">
    <!-- v-list-tile-title>{{word.text}}</v-list-tile-title -->
    <v-checkbox @click="filterWord" v-model="word.state" hide-details color="blue darken-4" :label="word.text"></v-checkbox>
    </v-list-tile>
    </v-list>
    </v-navigation-drawer>
    <v-layout  align-center justify-center column>
    <v-card v-for="post in posts" @click="post.is_look != post.is_look" :style="stylePost(post.is_look)">
    <v-card-title class="title">{{ post.title }}</v-card-title>
    <v-card-text>
    <p>
    <span class="type">{{ post.ptype.split('.')[1]}}</span>
    <span class="duration"> {{ post.duration}}</span>
    <span class="posted_time">{{ post.posted_time}}</span></p>
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
        axios.get('http://localhost:5000/api/v1/posts').then( o => { this.model = o.data; this.posts = this.model}).catch(e => console.error(e));
        axios.get('http://localhost:5000/api/v1/words').then( o => this.initWords(o.data)).catch(e => console.error(e));
    },
    methods:{
        initWords: function(words){
            words.forEach(o => {
                this.words.push({
                    id: o.id,
                    text: o.text,
                    state: true
                })
            })
        },
        filterWord: function(){
            this.posts =[];
           this.words.forEach(
                o => {
                    if(o.state === true){
                        this.model.forEach(v => {
                            if(parseInt(v.word_id) === o.id){
                                this.posts.push(v);
                            }
                        })}
                });
        },
        sortDateTime: function(){
            this.posts.sort(function(a,b){ return new Date(b.posted_time).getTime() - new Date(a.posted_time).getTime()});
        },
        stylePost: function(state){
            return {
                'max-width': '1200px',
                'min-width':'1200px',
            }
        }
    },
    data () {
        return {
            model:[],
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
