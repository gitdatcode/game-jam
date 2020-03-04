(function($, window){
    var body = $('body'),
        loaded_images = [],
        loaded_audio = [],
        loaded_scenes = {};

    function loadImage(src, callback){
        console.info('loading image', src)
        var idx = loaded_images.indexOf(src);

        if(idx > -1){
            var img = new Image();
            img.src = src;
        }

        callback();
    }

    function loadAudio(src, callback){
        console.info('loading audio', src)
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

            load: function(callback){
                callback = callback || function(){};
                var cb = function(){
                        this.playAudioBackground();
                        callback();
                    }.bind(this);

                this.show()
                    .preloadAssets()
                    .playAudioIntro(cb);

                return this;
            },

            unload: function(callback){
                callback = callback || function(){};
                var cb = function(){
                        this.stopAllAudio();
                        callback();
                    }.bind(this);

                this.hide()
                    .playAudioOutro(cb);

                return this;
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
                if(audio_intro.length){
                    audio_intro[0].addEventListener('ended', callback);
                    audio_intro[0].play();
                }else{
                    callback();
                }

                return this;
            },

            playAudioBackground: function(){
                if(audio_background.length){
                    audio_background[0].attr('loop', true);
                    audio_background[0].play();
                }

                return this;
            },

            playAudioOutro: function(callback){
                if(audio_outro.length){
                    audio_outro[0].play();
                }

                callback();

                return this;
            },

            stopAudioIntro: function(){
                if(audio_intro.length){
                    audio_intro[0].pause();
                }

                return this;
            },

            stopAudioBackground: function(){
                if(audio_background.length){
                    audio_background[0].pause();
                }

                return this;
            },

            stopAudioOutro: function(){
                if(audio_outro.length){
                    audio_outro[0].pause();
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
            console.info('loading scene ', scene.href);

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
