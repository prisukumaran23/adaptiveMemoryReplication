    // Version 3 pilot-3.1 (10 Participants on prolific)
    // Recognition memory study 
    // Rewards: 15p (green star) for high reward trials and 1p (grey star) for low reward trials
    // Total word-image pairs: 96

    // Create timelines 
    var timeline =[];
    var initiate_timeline = [];
    var rec_memory_timeline = [];
    var memory_timeline = []; 
    var end_timeline = [];

    // Experimental parameters 
    var TRIAL_REPETITIONS = 1; 
    var PARTICIPANT;
    var MOD;
    var WORDS=[];
    var WORDS_SHUFFLED='';
    var IMAGES=[];
    var IMAGES_SHUFFLED='';
    var HIGH_REWARD_CATEGORY;
    var CURRENT_CATEGORY;
    var SCORE = 0;
    var TOT = 0;
    var CORRECT_KEY='';
    var KEY_PRESS='';
    var PRESS='';
    var SHUFFLE_IMG_WORD=[];
    var MATCH_TYPE=[];
    var MATCH_CHOSEN_SCREEN='';
    
    var randomIndexes = [];
    var Shuffled_animals1=[]; 
    var Shuffled_objects1=[]; 
    for (var i=0; i<48; i++) {
      randomIndexes[i] = i;
    }
    randomIndexes.sort(function() {return (Math.round(Math.random())-0.5);});
   
    shuffle_sameindices = function(index,stim){
      out = []
      for (var i=0; i<48; i++) {
        out[i]=(stim[index[i]])}
      console.log(out)
      return out}

    add_phase_data = function(stimuli){
        for (var i=0; i<32; i++) {stimuli[i].phase = 'Phase1';}
        for (var i=32; i<64; i++) {stimuli[i].phase = 'Phase2';}
        for (var i=64; i<96; i++) {stimuli[i].phase = 'Phase3';}
    return stimuli}

   add_phase_data_recog = function(stimuli){
        phase1 = []; phase2 = []; phase3 = [];
        for (j=0; j<Stimuli_Phase1.length ; j++){
            phase1.push(Stimuli_Phase1[j].word)
            phase2.push(Stimuli_Phase2[j].word)
            phase3.push(Stimuli_Phase3[j].word)}
        for (k=0;k<288;k++){
            if (phase1.includes(stimuli[k].word)){
            stimuli[k].phase = 'Phase1';}
            else if (phase2.includes(stimuli[k].word)){ 
            stimuli[k].phase = 'Phase2';}
            else if (phase3.includes(stimuli[k].word)){
            stimuli[k].phase = 'Phase3';}}
    return stimuli} 

    Shuffled_animals1=shuffle_sameindices(randomIndexes,stimuli_animals1)
    Shuffled_objects1=shuffle_sameindices(randomIndexes,stimuli_objects1)

    var Stimuli_Memory_Unshuffled = [].concat(Shuffled_animals1.slice(0,16),Shuffled_objects1.slice(0,16),Shuffled_animals1.slice(16,32),Shuffled_objects1.slice(16,32),Shuffled_animals1.slice(32,),Shuffled_objects1.slice(32,));
    Stimuli_Memory_Unshuffled = add_phase_data(Stimuli_Memory_Unshuffled)
    
    var Stimuli_Memory = jsPsych.randomization.repeat(Stimuli_Memory_Unshuffled, 1);
    var Stimuli_Phase1 = jsPsych.randomization.repeat([].concat(Shuffled_animals1.slice(0,16),Shuffled_objects1.slice(0,16)),1);
    var Stimuli_Phase2 = jsPsych.randomization.repeat([].concat(Shuffled_animals1.slice(16,32),Shuffled_objects1.slice(16,32)),1);
    var Stimuli_Phase3 = jsPsych.randomization.repeat([].concat(Shuffled_animals1.slice(32,),Shuffled_objects1.slice(32,)),1);

    var Stim_Recog_Mem_Unshuffled = [].concat(old_img,old_word,new_img,new_word);
    Stim_Recog_Mem_Unshuffled = add_phase_data_recog(Stim_Recog_Mem_Unshuffled)
    var Stim_Recog_Mem = jsPsych.randomization.repeat(Stim_Recog_Mem_Unshuffled, 1);

    var Current_Phase;
    var REW_VAL;

    function roundNumber(number, decimals) {
        var newnumber = new Number(number+'').toFixed(parseInt(decimals));
        return parseFloat(newnumber);}

    count = 0;
    check_consecutive = function(stimuli) {
        count_cat = 0;count_word = 0;
        seq_cat = [];seq_word = [];
        for (i=0;i<31;i++){
            if (stimuli[i].category==stimuli[i+1].category){
              count_cat++;
              seq_cat.push(count_cat);} 
            else {count_cat=0;seq_cat.push(count_cat)}
            if (stimuli[i].word==stimuli[i+1].word){
              count_word++;
              seq_word.push(count_word);} 
            else {count_word=0;seq_word.push(count_word);}}
        if (seq_cat.some(el => el > 3 || seq_word.some(el => el > 0))){return false}
        else {count_cat=0;count_word=0;return true}}
    
    count2 = 0;
    check_consecutive_recog = function(stimuli) {
        count_type = 0; c_img = 0; c_word = 0;   
        seq_type = []; seq_img = []; seq_word = [];
        for (k=0;k<575;k++){
            if (stimuli[k].type==stimuli[k+1].type){
                count_type++;
                seq_type.push(count_type);} 
            else {count_type=0;seq_type.push(count_type)}
            if (stimuli[k].type=="old_img"||stimuli[k].type=="new_img" && stimuli[k+1].type=="old_img"||stimuli[k+1].type=="new_img"){
                c_img++;
                seq_img.push(c_img);} 
            else {c_img=0;seq_img.push(c_img);}}
        if (seq_type.some(el => el > 4)|| seq_img.some(el => el > 4)){return false}
        else {count_type=0;c_img=0;c_word=0;return true}}
    
    make_recog_stim = function(){
        count2 = 0;
        Stim_Recog_Mem = jsPsych.randomization.repeat(Stim_Recog_Mem,1);
        do{Stim_Recog_Mem = jsPsych.randomization.repeat(Stim_Recog_Mem,1);}
        while(check_consecutive_recog(Stim_Recog_Mem)==false);}

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

    make_stimuli_3 = function(){
        count = 0;
        Stimuli_Phase3 = jsPsych.randomization.repeat(Stimuli_Phase3,1)
        do{Stimuli_Phase3 = jsPsych.randomization.repeat(Stimuli_Phase3,1);}
        while(check_consecutive(Stimuli_Phase3)==false);}

    make_recog_stim(); make_stimuli_1(); make_stimuli_2(); make_stimuli_3();
    
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
          "<p> Welcome to day 2 of the guessing game.</p>"+
          "<p> Press the next button below or right arrow key to continue.</p>",
              "You can track your progress on the progress bar at the top of the screen which will be updated after each phase of the study.",
              "</p><p>Please ensure that you are in a quiet location without distractions and that you will not be interrupted."+ 
              "</p><p>Also, please ensure you are using a desktop PC or laptop and not a tablet or a phone."],
        show_clickable_nav: true};

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
        jsPsych.setProgressBar(0.05);
        Current_Phase = 'Rec_Memory';}};

    var instructions5 = {
      type: "html-keyboard-response",
      stimulus: 
      "</p><p>You will be presented with words and images one at a time."+
      "</p><p>Your task is to decide whether you have seen exactly this word or image from day 1 of the experiment (OLD) or not (NEW)."+
      "</p><p>You will make your responses using the following confidence scale:"+
      "</p><p><button class='btn-bigger'>Definitely old</button>&nbsp;&nbsp;<button class='btn-bigger'>Likely old</button>&nbsp;&nbsp;<button class='btn-bigger'>Maybe old</button>&nbsp;&nbsp;<button class='btn-bigger'>Maybe new</button>&nbsp;&nbsp;<button class='btn-bigger'>Likely new</button>&nbsp;&nbsp;<button class='btn-bigger'>Definitely new</button>"+
      "</p><p>It will take no more than 15 minutes and you will answer about 500 questions."+
      "</p><p><b>Press J</b> to begin the memory test.",
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'instructions'},
      on_finish: function(instructions5){
        jsPsych.setProgressBar(0.05);
        Current_Phase = 'Rec_Memory';}};
    
    var instructions6 = {
      type: "html-keyboard-response",
      stimulus: "Memory test completed."+
      "</p><p>The next part of the study is another surprise memory test."+
      "</p><p><b>Press J</b> to read the instructions.",
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'instructions'},
      on_finish: function(instructions6){
        jsPsych.setProgressBar(0.55);
        Current_Phase = 'Asc_Memory';}};
          
    var instructions7 = {
      type: "html-keyboard-response",
      stimulus: 
      "</p><p>You will be shown images from the day 1 and you will have to choose the <b>correct</b> Japanese word for that image."+
      "</p><p>Similar to guessing tasks from day 1, <b>Press F</b> for left word or <b>Press J</b> for right word to choose."+
      "</p><p>After choosing a word, you will be asked to rate how confident you are of your choice."+
      "</p><p>It will take no more than 5 minutes and you will answer about 90 questions."+
      "</p><p><b>Press J</b> to begin the final memory test.",
      trial_duration: 60000,
      choices: ['j'],
      data: {trial_id: 'instructions'},
      on_finish: function(instructions7){
        jsPsych.setProgressBar(0.55);
        Current_Phase = 'Asc_Memory';}};

    var fixation = {
        type: 'html-keyboard-response',
        stimulus: '<p style="font-size: 80px; font-family:monospace;">+</p>',
        choices: jsPsych.NO_KEYS,
        trial_duration: 1000,
        data: {trial_id: 'fixation'}}

    var image = {
        type: 'html-keyboard-response',
        stimulus: function(){
            var html = "<div class='header' align='center' style='font-size: 45px;'><b>"+jsPsych.timelineVariable('word', true)+"</b></div>";
            html += "<div class='Row'>"+
            "<div align='center' style='font-size: 45px;'class='Column'> </div>"+
            "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('image', true)+"' height='300px' width='300px'></div>"+
            "<div align='center' style='font-size: 45px;'class='Column'> </div>"+
            "</div>"
            return html;},
        choices: jsPsych.NO_KEYS,
        data: {phase: function(){return Current_Phase},trial_id: 'stimuli', category: jsPsych.timelineVariable('category'), 
              word: jsPsych.timelineVariable('word'),matchword: jsPsych.timelineVariable('matchword')},
        trial_duration: 2000}

    check_correct_key = function(check) {
        if(check == WORDS[0] && check == WORDS_SHUFFLED[0]){return 'f';} 
        else if(check == WORDS[0] && check ==! WORDS_SHUFFLED[0]){return 'j';}
        else if(check == IMAGES_SHUFFLED[0]){return 'f';} 
        else{return 'j';}
        };
            
    letter_conversion = function(letter) {
    if(letter == 'j'){
        return 74;}
    else if (letter =='f'){
        return 70;}};
        
        var Rec_Trial_Type = ''
        var Old_or_New = ''
        var rec_memory = {
            type: 'html-button-response',
            stimulus: function(){
                    if (jsPsych.timelineVariable('type', true)=="old_img"||jsPsych.timelineVariable('type', true)=="new_img"){Rec_Trial_Type='img'}
                    else if (jsPsych.timelineVariable('type', true)=="old_word"||jsPsych.timelineVariable('type', true)=="new_word"){Rec_Trial_Type='word'}
                    if (Rec_Trial_Type=='img'){
                        var html = "<div class='header' align='center' style='font-size: 18px;'><i>Is this image <b>old</b> or <b>new</b>?</i></div>";
                        html += "<div class='Row'>"+
                        "<div align='center' class='Column'><img src='"+jsPsych.timelineVariable('stim', true)+"' height='300px' width='300px'></div>"+
                        "</div><div class='spacing' align='center' style='font-size: 18px;'><i> </i></div>";}
                    else if (Rec_Trial_Type=='word'){
                        var html = "<div class='header' align='center' style='font-size: 18px;'><i>Is this word <b>old</b> or <b>new</b>?</i></div><span class='brlarge3'></span>";
                        html += "<span class='brlarge3'></span><span class='brlarge3'></span><div class='Row'>"+
                        "<div align='center' style='padding-bottom:0px;font-weight: bold; font-size: 45px;'class='Column'>"+jsPsych.timelineVariable('stim', true)+"</div>"+
                        "</div><div class='spacing' align='center' style='font-size: 18px;'><i> </i></div>"+
                        "<div style='padding-bottom:165px;'</div>";}
                    return html;},
            choices:['Definitely old', 'Likely old','Maybe old', 'Maybe new','Likely new','Definitely new'],
            trial_duration: 10000,
            button_html: '<button class="btn-bigger">%choice%</button>',
            data: {phase: function(){return Current_Phase}, trial_id: 'rec_memory',word_phase: jsPsych.timelineVariable('phase'),
                  word_type: jsPsych.timelineVariable('word_type'),img_or_word:function(){return Rec_Trial_Type},
                  type:jsPsych.timelineVariable('type'),stim:jsPsych.timelineVariable('stim'),word:jsPsych.timelineVariable('word'),category: jsPsych.timelineVariable('category')},
            on_finish: function(data){
                PRESS = data.button_pressed
                console.log(jsPsych.timelineVariable('type',true))
                console.log(data.button_pressed)
                if (jsPsych.timelineVariable('type',true)=="old_img"||jsPsych.timelineVariable('type',true)=="old_word"){
                  if(data.button_pressed == 0||data.button_pressed == 1||data.button_pressed == 2){
                    data.correct = true;
                  }else{data.correct = false;}}
                else if (jsPsych.timelineVariable('type',true)=="new_img"||jsPsych.timelineVariable('type',true)=="new_word"){
                  if(data.button_pressed == 3||data.button_pressed == 4||data.button_pressed == 5){
                    data.correct = true;
                  }else{data.correct = false;}}  
                console.log(data.correct)}}
            
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
              matchword: jsPsych.timelineVariable('matchword')},
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
        
          var rec_memory_feedback_slow = {
            type: 'html-keyboard-response',
            stimulus: function(){
            var html = "<div class='header' align='center' style='font-size: 30px;color: black;'><b>Too slow!</b></div>";
            return html},
          choices: jsPsych.NO_KEYS,
          data: {phase: function(){return Current_Phase},trial_id: 'rec_memory_feedback', category: jsPsych.timelineVariable('category'),
              word: jsPsych.timelineVariable('word'), word_phase: jsPsych.timelineVariable('phase'), 
              matchword: jsPsych.timelineVariable('matchword')},
          trial_duration: 1200}

          var memory_feedback_slow = {
          type: 'html-keyboard-response',
          stimulus: function(){
          var html = "<div class='header' align='center' style='font-size: 30px;color: black;'><b>Too slow!</b></div>";
          return html},
        choices: jsPsych.NO_KEYS,
        data: {phase: function(){return Current_Phase},trial_id: 'memory_feedback', category: jsPsych.timelineVariable('category'),
            word: jsPsych.timelineVariable('word'), word_phase: jsPsych.timelineVariable('phase'), 
            matchword: jsPsych.timelineVariable('matchword')},
        trial_duration: 1200}

        var if_node1 = {
            timeline: [memory_certainty],
            conditional_function: function(){
                if (KEY_PRESS == '70' || KEY_PRESS == '74'){return true;}
                else {return false;}}}

        var if_node2 = {
            timeline: [memory_feedback_slow],
            conditional_function: function(){
                if (KEY_PRESS == '70' || KEY_PRESS == '74'){return false;}
                else {return true;}}}

        var if_node_rm = {
            timeline: [rec_memory_feedback_slow],
            conditional_function: function(){
                if (PRESS == null){return true;}
                else {return false;}}}
    
    var memory_test = {
      timeline: [match_memory, if_node1, if_node2], 
      //timeline_variables: Stimuli_Memory.slice(0,1),
      timeline_variables: Stimuli_Memory,
      randomize_order: true,
      repetitions: 1}

    var rec_memory_test = {
        timeline: [rec_memory, if_node_rm], 
        //timeline_variables: Stim_Recog_Mem.slice(0,1),
        timeline_variables: Stim_Recog_Mem,
        randomize_order: false,
        repetitions: 1}

    var end_info = {
      type: "instructions",
      pages:[
        "All tests completed. Please answer a few feedback questions before submitting your data."
      ],
      show_clickable_nav: true,
      on_start: function(end_info){
        jsPsych.setProgressBar(0.9)},
      data: {trial_id: 'instructions'}};

    function saveData(name, data){
      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'write_data.php'); // 'write_data.php' is the path to the php file described above.
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify({filename: name, filedata: data}));
    }

    var pilot_questions1 = {
      type: 'survey-text',
      questions: [{prompt:"Q1. Did you have any knowledge of Japanese beforehand?",required:true,rows:1,columns:80},
      {prompt:"Q2. What strategy did you use for the first memory test?",required:true,rows:1,columns:80},
      {prompt:"Q3. What strategy did you use for the second memory test?",required:true,rows:3,columns:80},],
      preamble: '<b> <font size ="5"> Feedback </font></b>'+
      '<p> Please answer the questions below and click continue.</p>',
      data: {trial_id: 'feedback'}
    }; 

    var pilot_questions2 = {
      type: 'survey-text',
      questions: [{prompt:"Q4. Please rate your sleep quality last night from 1 (very bad) to 5 (very good):",required:true,rows:1,columns:80},
      {prompt:"Q5. Did you notice that there were two categories of images (animals and objects)?",required:true,rows:1,columns:80},
      {prompt:"Q6. Did you notice which category was rewarded with a higher bonus in phase 2 from day 1?",rows:3,columns:80}],
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
    "<br>To test this, you were rewarded for only one category (either animals or objects) during phase 2 of the experiment and not during phases 1 or 3, and later tested for memory/successful learning."+
    "<p>We also want to examine how learning and memory is affected by rewards in mood/depression disorders. Thus, the study included questionnaires asking about your mental health."+
     "<br>If you have any concerns about your mental health, please contact your GP. There are also other support networks available such as the Samaritans (UK): 116 123 (24-hour free to call helpline)."+
    "<p>If you still have questions about the study or would like to learn more, please contact Priyanka Sukumaran (ox19730@bristol.ac.uk)."],
      show_clickable_nav: true,
      on_start: function(ending){
        jsPsych.setProgressBar(1.0)},
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

    memory_timeline.push(instructions6);
    memory_timeline.push(instructions7);
    memory_timeline.push(memory_test);

    end_timeline.push(end_info);
    end_timeline.push(pilot_questions1);
    end_timeline.push(pilot_questions2);
    end_timeline.push({
      type: 'call-function',
      func: function(){
        saveData("Recog_Memory_Day2_Json", jsPsych.data.get().json());
      }
      });
    end_timeline.push(submit_prolific);
    end_timeline.push({
      type: 'fullscreen',
      fullscreen_mode: false
    });
    end_timeline.push(ending);

  var initiate = {timeline: initiate_timeline}
  var memory = {timeline: memory_timeline}
  var rec_memory = {timeline: rec_memory_timeline}
  var end = {timeline: end_timeline}

  // Pushing all timelines onto main timeline
  //timeline.push(initiate,phase1,phase2,phase3,survey,rec_memory,memory,end)
  timeline.push(initiate,rec_memory,memory,end)

  // Start the experiment 
  jsPsych.init({
      timeline: timeline,
      show_progress_bar: true,
      //auto_update_progress_bar: true,
      preload_images: preload_imgs,
      //on_finish: function(){jsPsych.data.displayData('json')}
      }); 