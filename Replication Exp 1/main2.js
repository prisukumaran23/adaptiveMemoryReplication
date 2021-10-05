      // Replication (Patil) study day 2

    // Create timelines 
    var timeline =[];
    var initiate_timeline = [];
    var rec_memory_timeline = [];
    var end_timeline = [];

    // Experimental parameters 
    var TRIAL_REPETITIONS = 1; 
    var PARTICIPANT;
    var MOD;
    var IMAGES=[];
    var IMAGES_SHUFFLED='';
    var HIGH_REWARD_CATEGORY;
    var CURRENT_CATEGORY;
    var SCORE = 0;
    var CORRECT_KEY='';
    var KEY_PRESS='';
    var PRESS='';
    
    var Stim_Recog_Mem_Unshuffled = [].concat(old_img,new_img);
    var Stim_Recog_Mem = jsPsych.randomization.repeat(Stim_Recog_Mem_Unshuffled, 1);

    var Current_Phase;
    var REW_VAL;

    function roundNumber(number, decimals) {
        var newnumber = new Number(number+'').toFixed(parseInt(decimals));
        return parseFloat(newnumber);}

    check_consecutive_recog = function(stimuli) {
        count_type = 0; 
        seq_type = []; 
        for (k=0;k<239;k++){
            if (stimuli[k].type==stimuli[k+1].type){
                count_type++;
                seq_type.push(count_type);} 
            else {count_type=0;seq_type.push(count_type)} 
        if (seq_type.some(el => el > 4)){return false}
        else {count_type=0;return true}}}
    
    make_recog_stim = function(){
        count2 = 0;
        Stim_Recog_Mem = jsPsych.randomization.repeat(Stim_Recog_Mem,1);
        do{Stim_Recog_Mem = jsPsych.randomization.repeat(Stim_Recog_Mem,1);}
        while(check_consecutive_recog(Stim_Recog_Mem)==false);}

    make_recog_stim(); 
    
    set_details = function() {
    PARTICIPANT=Math.abs(hashCode(jsPsych.data.getLastTrialData().values()[0].responses.trim()))%2}

    hashCode = function(this_id) {
        var hash = 0, i, chr;
        if (this_id.length === 0) return hash;
        for (i = 0; i < this_id.length; i++) {
          chr   = this_id.charCodeAt(i);
          hash  = ((hash << 5) - hash) + chr;
          hash |= 0; // Convert to 32bit integer
        }
        return hash;};

    var welcome = {
        type: "instructions",
        pages:[
          "<p> Welcome to day 2 of the study.</p>"+
          "<p> Press the next button below or right arrow key to continue.</p>",
              "You can track your progress on the progress bar at the top of the screen which will be updated after each phase of the study.",
              "</p><p>Please ensure that you are in a quiet location without distractions and that you will not be interrupted."+ 
              "</p><p>Also, please ensure you are using a desktop PC or laptop and not a tablet or a phone."],
        show_clickable_nav: true};

    // Participant ID to be entered
    var pno_block = {
    type: 'survey-text',
    questions: [{prompt:"Please enter your prolific ID. Please do not include any spaces.", name:'ParticipantID',required:true}],
    data: {trial_id: 'prolificID'},
    on_finish: function(data) {
        var mod = Math.abs(hashCode(data.responses.trim()))%2;
        var category = ['Animal','Object'];
        MOD = mod;
        if (mod == 0) {
            data.condition = 'Reward_Animals';}
        else {
            data.condition = 'Reward_Objects';}console.log(data.condition)}};
    
    var age = {
        type: 'survey-text',
        data: {
          trial_id: 'subject age'},
        questions: [{prompt: "Please enter your age:", name:'Age',required:true}],
        required: true,
        horizontal: true};
    
    var gender = {
      type: 'survey-multi-choice',
      data: {
        trial_id: 'subject gender'},
      questions: [{prompt:'Sex:', name:'Sex', options:['Female','Male','Prefer not to say'],required:true}],
      required: [true]};

    var instructions4 = {
      type: "html-keyboard-response",
      stimulus: "You will now complete a surprise memory test."+
      "</p><p><b>Press J</b> to read the instructions.",
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'instructions'},
      on_finish: function(instructions4){
        //jsPsych.setProgressBar(0.05);
        Current_Phase = 'Rec_Memory';}};

    var instructions5 = {
      type: "html-keyboard-response",
      stimulus: 
      "</p><p>You will be presented with images one at a time."+
      "</p><p>Your task is to decide whether you have seen exactly this image from day 1 of the experiment (OLD) or not (NEW)."+
      "</p><p>You will respond using a slider and choose between:"+
      "</p><p>Definitely old, Likely old, Maybe old, Maybe new, Likely new, Definitely new."+
      "</p><p>It will take no more than 15 minutes."+
      "</p><p><b>Press J</b> to begin the memory test.",
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'instructions'},
      on_finish: function(instructions5){
        //jsPsych.setProgressBar(0.05);
        Current_Phase = 'Rec_Memory';}};
    
    var fixation = {
        type: 'html-keyboard-response',
        stimulus: '<p style="font-size: 80px; font-family:monospace;">+</p>',
        choices: jsPsych.NO_KEYS,
        trial_duration: 1000,
        data: {trial_id: 'fixation'}}

    check_correct_key = function(check) {
        if(check == IMAGES_SHUFFLED[0]){return 'f';} 
        else{return 'j';}
        };
            
    letter_conversion = function(letter) {
    if(letter == 'j'){
        return 74;}
    else if (letter =='f'){
        return 70;}};
        
    var Old_or_New = ''
    var rec_memory = {
        type: 'html-slider-response',
        stimulus: function(){
                var html = "<div class='header' align='center' style='font-size: 18px;'><i>Is this image <b>old</b> or <b>new</b>?</i></div>";
                html += "<div class='Row'>"+
                "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('stim', true)+"' height='300px' width='300px'></div>"+
                "</div><div class='spacing' align='center' style='font-size: 18px;'><i> </i></div>";
                return html;},
        labels:['Definitely old', 'Likely old','Maybe old','','Maybe new','Likely new','Definitely new'],
        trial_duration: 10000,
        slider_width:720,
        start:30,
        min:0,
        max:72,
        step:12,
        require_movement: true,
        data: {phase: function(){return Current_Phase}, trial_id: 'rec_memory',
                type:jsPsych.timelineVariable('type'),stim:jsPsych.timelineVariable('stim'),category: jsPsych.timelineVariable('category'),stim_eng: jsPsych.timelineVariable('stim_english')},
        on_finish: function(data){
            PRESS = data.response
            console.log(jsPsych.timelineVariable('type',true))
            console.log(data.response)
            if (jsPsych.timelineVariable('type',true)=="old_img"){
                if(data.response == 0||data.response == 12||data.response == 24){
                data.correct = true;
                }else{data.correct = false;}}
            else if (jsPsych.timelineVariable('type',true)=="new_img"){
                if(data.response == 48||data.response == 60||data.response == 72){
                data.correct = true;
                }else{data.correct = false;}}  
            console.log(data.correct)}}
        
    var rec_memory_feedback_slow = {
        type: 'html-keyboard-response',
        stimulus: function(){
        var html = "<div class='header' align='center' style='font-size: 30px;color: black;'><b>Too slow!</b></div>";
        return html},
        choices: jsPsych.NO_KEYS,
        data: {phase: function(){return Current_Phase},trial_id: 'rec_memory_feedback', category: jsPsych.timelineVariable('category')},
        trial_duration: 1200}

    var if_node_rm = {
        timeline: [rec_memory_feedback_slow],
        conditional_function: function(){
            if (PRESS == null){return true;}
            else {return false;}}}

    var rec_memory_test = {
        timeline: [rec_memory, if_node_rm], 
        //timeline_variables: Stim_Recog_Mem.slice(0,3),
        timeline_variables: Stim_Recog_Mem,
        randomize_order: false,
        repetitions: 1}

    var end_info = {
      type: "instructions",
      pages:["All tests completed. Please answer a few feedback questions before submitting your data."],
      show_clickable_nav: true,
      data: {trial_id: 'instructions'}};

    function saveData(name, data){
      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'write_data.php'); // 'write_data.php' is the path to the php file described above.
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({filename: name, filedata: data}));
    }

    var pilot_questions1 = {
      type: 'survey-text',
      questions: [{prompt:"Q1. How surprised were you by the memory test?",required:true,rows:1,columns:80},
      {prompt:"Q2. What strategy did you use for the memory test?",required:true,rows:1,columns:80},
      {prompt:"Q3. Please rate your sleep quality last night from 1 (very bad) to 5 (very good):",required:true,rows:1,columns:80}],
      preamble: '<b> <font size ="5"> Feedback </font></b>'+
      '<p> Please answer the questions below and click continue.</p>',
      data: {trial_id: 'feedback'}
    }; 

    var pilot_questions2 = {
      type: 'survey-text',
      questions: [
      {prompt:"Q4. Did you notice that there were two categories of images (animals and objects)?",required:true,rows:1,columns:80},
      {prompt:"Q5. Did you notice which category was rewarded with a higher bonus from day 1?",rows:3,columns:80}],
      preamble: '<b> <font size ="5"> Feedback </font></b>'+
      '<p> Please answer the questions below and click continue to submit your data.</p>',
      data: {trial_id: 'feedback'}
    }; 

    var submit_prolific = {
      type: "html-keyboard-response",
      stimulus: "You have completed the study!"+
      "<p>Please click on the link below to confirm your submission to Prolific."+
      "<p><b><a href='https://app.prolific.co/submissions/complete?cc=2714E33E' target='_blank'>Click to submit</a></b>"+
      "</p><p><b>Press J</b> when submission is complete.</p>", 
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'end'},
      on_finish: function(submit_prolific){
        Current_Phase = 'End';}};

    var ending = {
      type: "instructions",
      pages:["Finished! Thank you for your time and for taking part in this study."+
    "<p>The purpose of this study is to investigate whether people’s memories of similar stimuli can be improved in retrospect or after receiving rewards for that stimuli category."+
    "<br>To test this, you were rewarded for only one category (either animals or objects) during one phase of the experiment, and later tested for memory/successful learning."+
    "<p>We also want to examine how learning and memory is affected by rewards in mood/depression disorders. Thus, the study included questionnaires asking about your mental health."+
     "<br>If you have any concerns about your mental health, please contact your GP. There are also other support networks available such as the Samaritans (UK): 116 123 (24-hour free to call helpline)."+
    "<p>If you still have questions about the study or would like to learn more, please contact Priyanka Sukumaran (ox19730@bristol.ac.uk)."],
      show_clickable_nav: true,
      data: {trial_id: 'ending'}};
 
    // timeline containing initial info and consent forms
    initiate_timeline.push(welcome);
    initiate_timeline.push(age);
    initiate_timeline.push(gender);
    initiate_timeline.push(pno_block);
    initiate_timeline.push({
    type: 'call-function',
    func: function(){
      set_details();}  // calls set_details function immediately after participant ID given
    });
    initiate_timeline.push({
      type: 'fullscreen',
      fullscreen_mode: true
    });

    rec_memory_timeline.push(instructions4);
    rec_memory_timeline.push(instructions5);
    rec_memory_timeline.push(rec_memory_test);

    end_timeline.push(end_info);
    end_timeline.push(pilot_questions1);
    end_timeline.push(pilot_questions2);
    end_timeline.push({
      type: 'call-function',
      func: function(){
        saveData("ReplicationPatil_Day2", jsPsych.data.get().json());
      }
      });
    end_timeline.push(submit_prolific);
    end_timeline.push({
      type: 'fullscreen',
      fullscreen_mode: false
    });
    end_timeline.push(ending);

  var initiate = {timeline: initiate_timeline}
  var rec_memory = {timeline: rec_memory_timeline}
  var end = {timeline: end_timeline}

  // Pushing all timelines onto main timeline
  timeline.push(initiate, rec_memory, end)

  // Start the experiment 
  jsPsych.init({
      timeline: timeline,
      show_progress_bar: false,
      preload_images: preload_imgs
      //on_finish: function(){jsPsych.data.displayData('json')}
      }); 