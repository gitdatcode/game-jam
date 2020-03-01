(function($, window){
    var body = $('body'),
        loaded_images = [],
        loaded_audio = [],
        loaded_scenes = {};

    function loadImage(src, callback){
        console.log('loading image', src)
        var idx = loaded_images.indexOf(src);

        if(idx > -1){
            var img = new Image();
            img.src = src;
        }

        callback();
    }

    function loadAudio(src, callback){
        console.log('loading audio', src)
        var idx = loaded_audio.indexOf(src);

        if(idx > -1){
            var audio = new Audio();
            audio.addEventListener('canplaythrough', callback, false);
            audio.src = url;
        }else{
            callback()
        }
    }

    function Scene(game, href, content, data){
        var scene = $(content),
            audio_intro = scene.find('.audio .intro'),
            audio_outro = scene.find('.audio .outro'),
            audio_background = scene.find('.audio .background'),
            scene_copy = scene.find('.scene_copy'),
            scene_option = scene.find('.scene_option');

        var instance = {
            href: href,
            content: scene,

            load: function(){
                this.show()
                    .preloadAssets()
                    .playAudioIntro(this.playAudioBackground.bind(this));
            },

            unload: function(){
                this.hide()
                    .playAudioOutro(this.stopAllAudio.bind(this));
            },

            show: function(){
                scene.show();
                game.main_container.append(scene);
                history.replaceState(data, '', href)

                return this;
            },

            hide: function(){
                scene.hide();

                return this;
            },

            preloadAssets: function(){
                if('scene' in data){
                    if('preload' in data['scene']){
                        if('audio' in data['scene']['preload']){
                            data['scene']['preload']['audio'].forEach(function(src){
                                loadAudio(src, () => {});
                            });
                        }
                
                        if('images' in data['scene']['preload']){
                            data['scene']['preload']['images'].forEach(function(src){
                                loadImage(src, () => {});
                            });
                        }
                    }
                }

                return this;
            },

            playAudioIntro: function(callback){
                if(audio_intro){

                }else{
                    callback();
                }

                return this;
            },

            playAudioBackground: function(){
                if(audio_background){
                    
                }

                return this;
            },

            playAudioOutro: function(callback){
                if(audio_outro){
                }

                callback();

                return this;
            },

            stopAudioIntro: function(){
                if(audio_intro){
                    audio_intro.stop();
                }

                return this;
            },

            stopAudioBackground: function(){
                if(audio_background){
                    audio_background.stop();
                }

                return this;
            },

            stopAudioOutro: function(){
                if(audio_outro){
                    audio_outro.stop();
                }

                return this;
            },

            stopAllAudio: function(){
                this.stopAudioIntro()
                    .stopAudioBackground()
                    .stopAudioOutro();

                return this;
            }
        };
        scene_option.on('click', function(e){
            e.preventDefault();

            game.loadScene(this.href);
        });
        console.log('>>>>>', scene, scene_option, '{{{{{{{')
        console.log(scene_option[0], jQuery._data(scene_option[0], "events" ));

        return instance;
    }

    function Game(){
        var main_container = $('.main_container'),
            loading_screen = $('.loading_screen'),
            initial_scene = $('.scene'),
            // mock scene
            active_scene = {
                href: "",
                unload: function(){}
            };

        function loadTheScene(scene){
            console.log("loading", scene);
            // debugger
            if(active_scene.href != scene.href){
                if(active_scene){
                    active_scene.unload();
                }

                loaded_scenes[scene.href] = scene;

                scene.load();
                active_scene = scene;
            }
        }

        var game = {
            main_container: main_container, 

            loadingScreen: function(show){
                // TODO: change this to be a fancy css transition
                loading_screen.css('display', show ? 'block' : 'none');

                return this;
            },

            loadScene: function(href){
                if (href in loaded_scenes){
                    loadTheScene(loaded_scenes[href]);

                    return this;
                }

                var game = this;

                $.ajax({
                    dataType: 'json',
                    url: href,
                    method: 'get',
                    success: function(resp, status, xhr){
                        var new_scene = new Scene(game, href, resp['content'], resp['scene']);
                        loadTheScene(new_scene);
                    },
                    error: function(xhr, status, error){

                    }
                });

                return this;
            }
        };

        if(initial_scene){
            var new_scene = new Scene(game, window.location.pathname, initial_scene, {});
            loadTheScene(new_scene);
        }

        return game;
    }

    window.Game = new Game();
}(jQuery, window));