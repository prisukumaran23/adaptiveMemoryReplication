    // Replication (Patil) study day 1

    // Create timelines 
    var timeline =[];
    var initiate_timeline = [];
    var phase1_timeline = [];
    var phase2_timeline = [];
    var survey_timeline = [];
    var end_timeline = [];

    // Experimental parameters 
    var TRIAL_REPETITIONS = 1; 
    var PARTICIPANT;
    var MOD;
    var IMAGES=[];
    var IMAGES_SHUFFLED='';
    var HIGH_REWARD_CATEGORY;
    var CURRENT_CATEGORY;
    var SCORE_HIGH = 0;
    var SCORE_LOW = 0;
    var CORRECT_KEY='';
    var KEY_PRESS='';
    var TOO_SLOW = 0;

    var randomIndexes = [];
    var Shuffled_animals1=[]; 
    var Shuffled_objects1=[]; 
    for (var i=0; i<60; i++) {
      randomIndexes[i] = i;
    }
    randomIndexes.sort(function() {return (Math.round(Math.random())-0.5);});
   
    shuffle_sameindices = function(index,stim){
      out = []
      for (var i=0; i<60; i++) {
        out[i]=(stim[index[i]])}
      console.log(out)
      return out}

    add_phase_data = function(stimuli){
        for (var i=0; i<60; i++) {stimuli[i].phase = 'Phase1';}
        for (var i=60; i<120; i++) {stimuli[i].phase = 'Phase2';}
    return stimuli}

    Shuffled_animals1=shuffle_sameindices(randomIndexes,stimuli_animals1)
    Shuffled_objects1=shuffle_sameindices(randomIndexes,stimuli_objects1)

    var Stimuli_Memory_Unshuffled = [].concat(Shuffled_animals1.slice(0,30),Shuffled_objects1.slice(0,30),Shuffled_animals1.slice(30,),Shuffled_objects1.slice(30,));
    Stimuli_Memory_Unshuffled = add_phase_data(Stimuli_Memory_Unshuffled)
    
    var Stimuli_Memory = jsPsych.randomization.repeat(Stimuli_Memory_Unshuffled, 1);
    var Stimuli_Phase1 = jsPsych.randomization.repeat([].concat(Shuffled_animals1.slice(0,30),Shuffled_objects1.slice(0,30)),1);
    var Stimuli_Phase2 = jsPsych.randomization.repeat([].concat(Shuffled_animals1.slice(30,),Shuffled_objects1.slice(30,)),1);

    var Current_Phase;
    var REW_VAL;

    function roundNumber(number, decimals) {
        var newnumber = new Number(number+'').toFixed(parseInt(decimals));
        return parseFloat(newnumber);}

    count = 0;
    check_consecutive = function(stimuli) {
        count_cat = 0;
        seq_cat = [];
        for (i=0;i<59;i++){
            if (stimuli[i].category==stimuli[i+1].category){
                count_cat++;
                seq_cat.push(count_cat);
                } 
            else {count_cat=0;seq_cat.push(count_cat)}
        if (seq_cat.some(el => el > 3)){return false}
        else {count_cat=0;return true}}}
    
    make_stimuli_1 = function(){
        count = 0;
        Stimuli_Phase1 = jsPsych.randomization.repeat(Stimuli_Phase1,1);
        do{Stimuli_Phase1 = jsPsych.randomization.repeat(Stimuli_Phase1,1);}
        while(check_consecutive(Stimuli_Phase1)==false);}
    
    make_stimuli_2 = function(){
        count = 0;
        Stimuli_Phase2 = jsPsych.randomization.repeat(Stimuli_Phase2,1)
        do{Stimuli_Phase2 = jsPsych.randomization.repeat(Stimuli_Phase2,1);}
        while(check_consecutive(Stimuli_Phase2)==false);}

    make_stimuli_1(); make_stimuli_2(); 
    
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

    var setreward ={
        type: 'call-function',
        func: function(){
            var category = ['Animal','Object'];
            if (PARTICIPANT == 0){
              HIGH_REWARD_CATEGORY = category[0]}
            else {
              HIGH_REWARD_CATEGORY = category[1]}}}

    var welcome = {
    type: "instructions",
    pages:[
        "<p> Welcome to day 1 of the study.</p>"+
        "<p> Press the next button below or right arrow key to continue.</p>",
        "<p>Please read the following information to decide if you are happy to participate in this study.</p>",
        "<p>This is a 2 day study."+
        "<p>Today, you will complete 2 phases with a break in between.</p>"+
        "<p> In each phase, you will be shown trials with a cue image, then after a delay, you will be presented with two images."+
        "<br>Your goal is to determine which of these two images matches the original cue image as quickly as possible.",
        "<p> In one of the phases, you will have the opportunity to win bonus payments"+
        "<br>for correct matching performance.</p>"+
            "<p>Following the 2 phases, you will be asked to complete a survey about your mood.",
            "<p>After 24 hours, you will be invited to day 2 of the study via your prolific inbox.</p>"+
            "<p>Please note that you will need to complete day 2 within 1-2 hours of receiving the invite.",
            "<p>Today's session should take about 30 minutes, and day 2 should take about 15 minutes.</p>"+
            "<p>Please note that you will only receive payment if you complete <b>both days</b> of the study.</p>",
            "You can track your progress on the progress bar at the top of the screen which will be updated after each phase of the study."+
            "</p><p>Please ensure that you are in a quiet location without distractions and that you will not be interrupted."+ 
            "</p><p>Also, please ensure you are using a desktop PC or laptop and not a tablet or a phone.",
            "</p><p>If you are happy with the information, press next to complete a consent form.</p>"],
    show_clickable_nav: true};

    // Define instructions trial 
    var instructions1 = {
        type: "instructions",
        pages:[
            "<p> Let's begin the study. </p><p> You will be shown an image, which will be followed by a 5s delay with a fixation cross."+
            "<br>You will then be shown two images and you must choose the original image as <b>quickly</b> as you can by:" +
            "</p><p><b>Pressing F</b> to select left or <b>Pressing J</b> to select right."+
            "</p><p>Let's try some practice trials first. Press next to begin."],
        show_clickable_nav: true,
        on_finish: function(instructions){
            Current_Phase = 'Trial';}};

    // Ensure check box in consent form is checked, otherwise alert pops up
    var check_consent = function(elem) {
    if (document.getElementById('consent_checkbox').checked) {return true;}
    else {alert("If you wish to participate, you must check the box 'I have read and understood the information provided and agree to take part in this study'.");
      return false;}
    return false;};

    // Consent 
    var consent = {
    type:'external-html',
    url: "consent_external_page.html",
    cont_btn: "start",
    check_fn: check_consent}; 

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
            data.condition = 'Reward_Objects';}}};
    
    set_score = function(SCORE_HIGH,SCORE_LOW){
        if(SCORE_HIGH>=27 && SCORE_LOW>=27){
            bonus = 5.25}
        else if(SCORE_HIGH>=27){bonus = 5.00}
        else if(SCORE_LOW>=27){bonus = 0.25}
        else{bonus = 0}
        return bonus;
        };

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

    var instructions2 = {
        type: "html-keyboard-response",
        stimulus: "<p>Now let's begin the real study.</p><p>Phase 1 will take no more than 12 minutes."+
        "</p><p><b>Press J</b> to begin.</p>", 
        trial_duration: 60000,
        choices: ['j'],
        data: {trial_id: 'instructions'},
        on_start: function(instructions2){
          jsPsych.setProgressBar(0.10);},
        on_finish: function(instructions2){
          Current_Phase = 'Phase 1';}};

    var instructions3 = {
        type: "html-keyboard-response",
        stimulus: "<p>In this phase you can earn rewards."+
        "</p><p>Correct matching performance of 90% or more on “green star” trials will result in a £5 bonus,"+
        "<br>whereas a performance of 90% or more on the “grey star” trials will result in a £0.25 bonus."+
        "<p> The indicative stars are shown below for reference."+
        "<div style='width: 750px;'>"+
        "<div style='float: left;'><img src='../img/greenstar.jpg' height='250px' width='250px' align='middle'></img>" +
        "<p class='small'>Green star</p></div>" +
        "<div style='float: right;'><img src='../img/greystar.jpg' height='250px' width='250px' align='middle'></img>" +
        "<p class='small'>Grey star</p></div>" +
        "</div>"+
        "<div class='space'></div></p><p>Phase 1 will take no more than 12 minutes."+
        "</p><p><b>Press J</b> to begin.", 
        trial_duration: 60000,
        data: {trial_id: 'instructions'},
        choices: ['j'],
        on_finish: function(instructions3){
            jsPsych.setProgressBar(0.10);
            Current_Phase = 'Phase 1';}};
        
    var instructions_break_1 = {
        type: "html-keyboard-response",
        stimulus: "<p>You have completed phase 1. Your bonuses will be calculated and paid after completing day 2."+
        "</p><p>Now you may take a break for a few minutes (not more than 3 minutes)."+
        "</p><p><b>Press J</b> when you are ready to continue to the next phase.</p>"+ 
        "</p><p><br><b>Note: </b>The study will move onto the next page automatically after 3 minutes.",
        trial_duration: 180000,
        data: {trial_id: 'instructions'},
        choices: ['j'],
        on_start: function(instructions_break_1){
            jsPsych.setProgressBar(0.55);},
        on_finish: function(instructions_break_1){
            Current_Phase = 'Phase 2';}};

    var instructions4 = {
        type: "html-keyboard-response",
        stimulus: "<p>Phase 2 will be the same as Phase 1 but there are no rewards."+
        "</p><p>Phase 2 will take no more than 12 minutes."+
        "</p><p><b>Press J</b> to begin.</p>", 
        trial_duration: 60000,
        choices: ['j'],
        data: {trial_id: 'instructions'},
        on_start: function(instructions2){
            jsPsych.setProgressBar(0.55);},
        on_finish: function(instructions4){
            Current_Phase = 'Phase 2';}};
        
    var instructions_break_2 = {
      type: "html-keyboard-response",
      stimulus: function(){
      var html = "<p>Great job! You have completed phase 2 of learning.";
      html +=  "</p><p><b>Press J</b> when you are ready to continue to the final part of the study.</p>"+
      "</p><p><br><b>Note: </b>The study will move onto the next page automatically after 1 minute."; 
      return html},
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'instructions'},
      on_start: function(instructions_break_2){
        jsPsych.setProgressBar(0.85);},
      on_finish: function(instructions_break_2){
        Current_Phase = 'Phase 2';}};

    var instructions5 = {
    type: "html-keyboard-response",
    stimulus: "In the next part of the study you will complete a survey about your mood over the past 2 weeks."+
    "</p><p><b>Press J</b> to begin the survey.",
    trial_duration: 60000,
    choices: ['j'],
    data: {trial_id: 'instructions'},
    on_finish: function(instructions5){
        jsPsych.setProgressBar(0.85);
        Current_Phase = 'Survey';}};

    var fixation = {
        type: 'html-keyboard-response',
        stimulus: '<p style="font-size: 80px; font-family:monospace;">+</p>',
        choices: jsPsych.NO_KEYS,
        trial_duration: 5000,
        data: {trial_id: 'fixation'}}

    var image = {
        type: 'html-keyboard-response',
        stimulus: function(){
            var html = "<div class='Row'>"
            html += "<div align='center' style='font-size: 45px;'class='Column'> </div>"+
            "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('image', true)+"' height='300px' width='300px'></div>"+
            "<div align='center' style='font-size: 45px;'class='Column'> </div>"+
            "</div>"
            return html;},
        choices: jsPsych.NO_KEYS,
        data: {phase: function(){return Current_Phase},trial_id: 'stimuli', category: jsPsych.timelineVariable('category'),stim_eng: jsPsych.timelineVariable('stim_english'),
        alt_eng:jsPsych.timelineVariable('alt_english')},
        trial_duration: 2000}

    check_correct_key = function(check) {
        if(check == IMAGES_SHUFFLED[0]){return 'f';} 
        else{return 'j';}
        };
            
    letter_conversion = function(letter) {
    if(letter == 'j'){
        return 74;}
    else if (letter =='f'){
        return 70;}};

    var match ={
        type: 'html-keyboard-response',
        stimulus: function(){
            IMAGES = [jsPsych.timelineVariable('image', true),jsPsych.timelineVariable('imagealt', true)];
            IMAGES_SHUFFLED = jsPsych.randomization.repeat(IMAGES, 1);
            check = IMAGES[0]
            console.log(check);  
                var html = "<div class='header' align='center' style='font-size: 18px;'><i></i></div>";
                html += "<div class='Row'>"+
                "<div align='center' style='padding-left:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[0]+"' height='300px' width='300px'class='white_border'><br/><br/>"+
                "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
                "<div align='center' style='padding-right:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[1]+"' height='300px' width='300px'class='white_border'><br/><br/>"+
                "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
                "</div>"
            return html;},
        data: {phase: function(){return Current_Phase},trial_id:'match',category: jsPsych.timelineVariable('category'),stim_eng: jsPsych.timelineVariable('stim_english'),
        alt_eng:jsPsych.timelineVariable('alt_english')},
        on_finish: function(data){
            var correct_letter = letter_conversion(check_correct_key(check))
            data.correct_key = correct_letter
            CORRECT_KEY = correct_letter
            KEY_PRESS = data.key_press
            if(data.key_press == correct_letter){
                data.correct = true
                console.log('correct');
            }else{
                data.correct = false
                console.log('wrong');}},
        choices: ['f','j'],
        trial_duration: 600}

    var match_memory ={
        type: 'html-keyboard-response',
        stimulus: function(){
            WORDS = [jsPsych.timelineVariable('word', true),jsPsych.timelineVariable('matchword', true)];
            WORDS_SHUFFLED = jsPsych.randomization.repeat(WORDS, 1);
            check = WORDS[0];
            var html = "<div class='header' align='center' style='font-size: 18px;'><i>Choose the correct word</i></div>";
            html += "<div class='Row'>"+
            "<div align='center' style='padding-left:200px; font-weight: bold; font-size: 45px;'class='Column'>"+WORDS_SHUFFLED[0]+"<br/><br/>"+
            "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
            "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('image', true)+"' height='300px' width='300px'></div>"+
            "<div align='center' style='padding-right:200px; font-weight: bold; font-size: 45px;'class='Column'>"+WORDS_SHUFFLED[1]+"<br/><br/>"+
            "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
            "</div>"+
            "<div class='header_mem' align='center' style='font-size: 18px;'><i> </i></div>";
            return html;},
        data: {phase: function(){return Current_Phase},trial_id:'match_memory',trial_matchtype:jsPsych.timelineVariable('matchtype'),category: jsPsych.timelineVariable('category'),
            word: jsPsych.timelineVariable('word'), word_phase: jsPsych.timelineVariable('phase'), 
            matchword: jsPsych.timelineVariable('matchword'),imagealt: jsPsych.timelineVariable('imagealt')},
        on_finish: function(data){
            var correct_letter = letter_conversion(check_correct_key(check))
            data.correct_key = correct_letter
            CORRECT_KEY = correct_letter
            KEY_PRESS = data.key_press
            if(data.key_press == correct_letter){
                data.correct = true;
            }else{
                data.correct = false;}},
        choices: ['f','j'],
        trial_duration: 5000}

    var memory_certainty = {
        type: 'html-button-response',
        stimulus: function(){
            if(KEY_PRESS == '70'){
                var html = "<div style='font-size: 20px;'<p>How confident are you of your choice?</p></div>";
                html += "<div class='Row'>"+
                "<div align='center' style='padding-left:200px; font-weight: bold; font-size: 45px;'class='Column'><u>"+WORDS_SHUFFLED[0]+"</u><br/><br/>"+
                "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
                "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('image', true)+"' height='300px' width='300px'></div>"+
                "<div align='center' style='padding-right:200px; font-weight: bold; font-size: 45px;'class='Column'>"+WORDS_SHUFFLED[1]+"<br/><br/>"+
                "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
                "</div>"
                return html;}
            else if (KEY_PRESS == '74'){
                var html = "<div style='font-size: 20px;'<p>How confident are you of your choice?</p></div>";
                html += "<div class='Row'>"+
                "<div align='center' style='padding-left:200px; font-weight: bold; font-size: 45px;'class='Column'>"+WORDS_SHUFFLED[0]+"<br/><br/>"+
                "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
                "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('image', true)+"' height='300px' width='300px'></div>"+
                "<div align='center' style='padding-right:200px; font-weight: bold; font-size: 45px;'class='Column'><u>"+WORDS_SHUFFLED[1]+"</u><br/><br/>"+
                "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
                "</div>"
                return html;}},
        choices:['Definitely guessing', 'Mostly guessing', 'Mostly certain','Definitely certain'],
        trial_duration: 20000,
        button_html: '<button class="btn-bigger">%choice%</button>',
        data: {phase: function(){return Current_Phase}, trial_id: 'memory_certainty'}}
    
    var memory_feedback_slow = {
        type: 'html-keyboard-response',
        stimulus: function(){
        var html = "<div class='header' align='center' style='font-size: 30px;color: black;'><b>Too Slow!</b></div>";
        return html},
    choices: jsPsych.NO_KEYS,
    data: {phase: function(){return Current_Phase},trial_id: 'memory_feedback', category: jsPsych.timelineVariable('category'),
        word: jsPsych.timelineVariable('word'), word_phase: jsPsych.timelineVariable('phase'), 
        matchword: jsPsych.timelineVariable('matchword')},
    trial_duration: 1200}

    var feedback ={
        type: 'html-keyboard-response',
        stimulus: function(){
        var red = '#d61818';
        var green = '#1f971f';
        var stim = ["<div class='Row'>"+
        "<div align='center' style='padding-left:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[0]+"' height='300px' width='300px'class='green_border'><br/><br/>"+
        "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
        "<div align='center' style='padding-right:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[1]+"' height='300px' width='300px'class='red_border'><br/><br/>"+
        "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
        "</div>","<div class='Row'>"+
        "<div align='center' style='padding-left:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[0]+"' height='300px' width='300px'class='red_border'><br/><br/>"+
        "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
        "<div align='center' style='padding-right:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[1]+"' height='300px' width='300px'class='green_border'><br/><br/>"+
        "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
        "</div>",
        "<div class='Row'>"+
        "<div align='center' style='padding-left:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[0]+"' height='300px' width='300px'class='white_border'><br/><br/>"+
        "<img src='../img/F.jpg' height='40px' width='40px'></div>"+
        "<div align='center' style='padding-right:150px; font-weight: bold; font-size: 45px;'class='Column'><img src='"+IMAGES_SHUFFLED[1]+"' height='300px' width='300px'class='white_border'><br/><br/>"+
        "<img src='../img/J.jpg' height='40px' width='40px'></div>"+
        "</div>"];
    if(KEY_PRESS == '70'& KEY_PRESS == CORRECT_KEY){
        var html = "<div class='header' align='center' style='font-size: 30px;color: "+green+";'><b></b></div>"+stim[0]+"";
        return html;}
    else if (KEY_PRESS == '74' & KEY_PRESS == CORRECT_KEY){
        var html = "<div class='header' align='center' style='font-size: 30px;color: "+green+";'><b></b></div>"+stim[1]+"";
        return html;}
    else if (KEY_PRESS == '74' & KEY_PRESS != CORRECT_KEY){
        var html = "<div class='header' align='center' style='font-size: 30px;color: "+red+";'><b></b></div>"+stim[0]+"";
        return html;}
    else if (KEY_PRESS == '70' & KEY_PRESS != CORRECT_KEY){
        var html = "<div class='header' align='center' style='font-size:30px;color: "+red+";'><b></b></div>"+stim[1]+"";
        return html;}
    else if (KEY_PRESS != CORRECT_KEY){
        TOO_SLOW += 1
        var html = "<div class='header' align='center' style='font-size: 30px;color: black;'><b>Too slow!</b></div>"+stim[2]+"";}
    else {TOO_SLOW += 1
        var html = "<div class='header' align='center' style='font-size: 30px;color: black;'><b>Too slow!</b></div>"+stim[2]+"";}
        return html},
    choices: jsPsych.NO_KEYS,
    data: {phase: function(){return Current_Phase},trial_id: 'feedback', category: jsPsych.timelineVariable('category'),stim_eng: jsPsych.timelineVariable('stim_english'),
    alt_eng:jsPsych.timelineVariable('alt_english')},
    trial_duration: 1000}

    set_outcome = function(key_press,correct_key) {
      var red = '#d61818';
      var green = '#1f971f';
      CURRENT_CATEGORY = jsPsych.data.getLastTrialData().values()[0].category;
      console.log(CURRENT_CATEGORY)
      if(HIGH_REWARD_CATEGORY == CURRENT_CATEGORY && key_press == correct_key){
        SCORE_HIGH++
          console.log('high rew cat',SCORE_HIGH)
            var html = "<div style='font-size: 30px; color:"+green+";'><p><b>Hit! You won:</b></div>";
            html += "<div style='padding-bottom:100px;' class='frame'><span class='helper'></span><img src='../img/greenstar.jpg' style='vertical-align:middle' height='240px' width='240px'></div>";
            return html;}
      else if(HIGH_REWARD_CATEGORY != CURRENT_CATEGORY && key_press == correct_key){ //correct but unrewarded category
        SCORE_LOW++
        console.log('low rew cat',SCORE_LOW)
        var html = "<div style='font-size: 30px; color:black;'><p><b>Hit! You won:</b></div>";
        html += "<div style='padding-bottom:100px;' class='frame'><span class='helper'></span><img src='../img/greystar.jpg' style='vertical-align:middle' height='240px' width='240px'></div>";
        return html;}
      else if(key_press == null){ //too slow
        var html="<div style='padding-top:10px; font-size: 30px; color:"+red+";''<p><b>Too slow!</b></p></div>";
        return html;}
      else{ //wrong
        var html="<div style='padding-top:10px; font-size: 30px; color:"+red+";''<p><b>Wrong!</b></p></div>";
        return html;}}

    var reward ={
      type: 'html-keyboard-response',
      stimulus: function(){
          var outcome = set_outcome(KEY_PRESS,CORRECT_KEY)
          return outcome},
      data: {reward_value: function(){return REW_VAL},phase: function(){return Current_Phase},trial_id: 'reward', category: jsPsych.timelineVariable('category'),
      word: jsPsych.timelineVariable('word'), 
      matchword: jsPsych.timelineVariable('matchword')},
      choices: jsPsych.NO_KEYS,
      trial_duration: 1100}

    var trial = {
      timeline: [image, fixation, match, feedback],
      timeline_variables: stimuli_trial,
      randomize_order: true}
    
    var trials_tooslow = {
        type: "html-keyboard-response",
        stimulus: "You were too slow. Please try again for few more rounds."+
        "</p><p>Be ready by placing your fingers on the <b>F and J keys</b> on your keyboard, and respond as quickly as possible!"+
        "</p><p><b>Press J</b> to begin.",
        trial_duration: 60000,
        choices: ['j'],
        data: {trial_id: 'instructions'},
        on_finish: function(trials_tooslow){;
            Current_Phase = 'Survey';}};

    var if_trial_node1 = {
    timeline: [trials_tooslow],
    conditional_function: function(){
        if (TOO_SLOW > 2){return true;}
        else {return false;}}
    }

    var if_trial_node2 = {
    timeline: [trial],
    conditional_function: function(){
        if (TOO_SLOW > 2){TOO_SLOW=0, 
            console.log(TOO_SLOW)
            return true;}
        else {return false;}}
    }

    var trials = {
        timeline: [trial, if_trial_node1, if_trial_node2],
    }

    var test_2 = {
      timeline: [image, fixation, match, feedback],
      timeline_variables: Stimuli_Phase1,
      //timeline_variables: Stimuli_Phase1.slice(0,1),
      randomize_order: false,
      repetitions: TRIAL_REPETITIONS}
    
    var test_1_reward = {
      timeline: [fixation, image, fixation, match, reward],
      timeline_variables: Stimuli_Phase2,    
      //timeline_variables: Stimuli_Phase2.slice(0,1),
      randomize_order: false,
      repetitions: TRIAL_REPETITIONS}

    var survey_ques = {
        type: 'html-slider-response',
        stimulus: function(){
            var html = "<div style='font-size: 16px;'<p>Over the last 2 weeks, how often have you been bothered by this problem?</p></div>"+
            "<div style='font-size:25px;'<p>"+jsPsych.timelineVariable('question',true)+"</p></div>";
            return html},
        labels: function(){return jsPsych.timelineVariable('labels',true)},
        data: {phase: function(){return Current_Phase}, trial_id: 'survey'},
        require_movement: true,
        slider_width: 700}
        
    var final_ques = {
        type: 'html-slider-response',
        stimulus: "<div style='font-size: 25px;'<p>If you have experienced any of the problems, how <b>difficult</b>"+
        "<br>have these problems made it for you to do your work, take care of things at home,"+ 
        "<br>or get along with other people?</p></div>",
        labels: ['Not difficult at all','Somewhat difficult','Very difficult','Extremely difficult'],
        slider_width: 700,
        data: {phase: function(){return Current_Phase}, trial_id: 'survey'},
        require_movement: true}

    var survey = {
        timeline: [survey_ques],
        timeline_variables: phq9,
        randomize_order: false}

    function saveData(name, data){
      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'write_data.php'); // 'write_data.php' is the path to the php file described above.
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({filename: name, filedata: data}));
    }

    var submit_prolific = {
      type: "html-keyboard-response",
      stimulus: "You have completed day 1 of the study!"+
      "<p>Please click on the link below to confirm your submission to Prolific."+
      "<p><b><a href='https://app.prolific.co/submissions/complete?cc=2714E33E' target='_blank'>Click to submit</a></b>"+
      "</p><p><b>Press J</b> when submission is complete.</p>", 
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'end'},
      on_finish: function(submit_prolific){
        Current_Phase = 'End';}};

    var end1 = {
        type: "instructions",
        pages:["Thank you for your time."+
        "<p>You will be invited to day 2 of the study via your prolific inbox in 24 hours."+
        "<p>Please note that you will only recieve payment if you complete day 2 as well."+
        "<p>Press next to finish."],
        show_clickable_nav: true,
        on_start: function(end){
            jsPsych.setProgressBar(1.0)},
        data: {trial_id: 'end1'}};
      
    var end2 = {
        type: "instructions",
        pages:["End of day 1."+
        "<p>You may now close the browser."],
        show_clickable_nav: true,
        on_start: function(end){
        jsPsych.setProgressBar(1.0)},
        data: {trial_id: 'end2'}};

    // timeline containing initial info and consent forms
    initiate_timeline.push(welcome);
    initiate_timeline.push(consent);
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
    initiate_timeline.push(instructions1);
    initiate_timeline.push(trials);
    initiate_timeline.push(setreward);

    phase1_timeline.push(instructions2);
    phase1_timeline.push(instructions3);
    phase1_timeline.push(test_1_reward);
    phase1_timeline.push(instructions_break_1);
    phase2_timeline.push(instructions4);
    phase2_timeline.push(test_2);
    phase2_timeline.push(instructions_break_2);

    survey_timeline.push(instructions5);
    survey_timeline.push(survey);
    survey_timeline.push(final_ques);

    end_timeline.push({
        type: 'call-function',
        func: function(){
          saveData("ReplicationPatilX2_Day1", jsPsych.data.get().json());
        }
        });
      end_timeline.push(submit_prolific);
      end_timeline.push({
        type: 'fullscreen',
        fullscreen_mode: false
      });
    end_timeline.push(end1);
    end_timeline.push(end2);

  var initiate = {timeline: initiate_timeline}
  var phase1 = {timeline: phase1_timeline}
  var phase2 = {timeline: phase2_timeline}
  var survey = {timeline: survey_timeline}
  var end = {timeline: end_timeline}

  // Pushing all timelines onto main timeline
  //timeline.push(initiate,phase1)
  timeline.push(initiate,phase1,phase2,survey,end)

  // Start the experiment 
  jsPsych.init({
      timeline: timeline,
      show_progress_bar: true,
      auto_update_progress_bar: false,
      preload_images: preload_imgs
      //on_finish: function(){jsPsych.data.displayData('json')}
    })
