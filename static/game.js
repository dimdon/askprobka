//Create the renderer
var renderer = PIXI.autoDetectRenderer(800, 600);
renderer.backgroundColor = 0xeeeeee;

//Add the canvas to the HTML document
document.body.appendChild(renderer.view);

//Create a container object called the `stage`
var stage = new PIXI.Container();

//Tell the `renderer` to `render` the `stage`
renderer.render(stage);

// ------------------------

var car;
var state;
var lanes = [];
var laneNumber = 0;
var road;
var lastUpdate = Date.now();
var message;

PIXI.loader
  .add("car.png")
  .add("car2.png")
  .load(setup);

//This `setup` function will run when the image has loaded
function setup() {

  road = new PIXI.Container();
  road.vy = 4;
  road.rheight = 80;
  road.gutter = 40;

  for (var rx = 10; rx <= 340; rx += 110) {
    for (var ry = -(road.rheight + road.gutter); ry < 600; ry += road.rheight + road.gutter) {
      var rectangle = new PIXI.Graphics();
      rectangle.beginFill(0xFFFFFF);
      rectangle.drawRect(0, 0, 10, road.rheight);
      rectangle.endFill();
      rectangle.x = rx;
      rectangle.y = ry;
      road.addChild(rectangle);
    }
  }
  stage.addChild(road);

  car = new PIXI.Sprite(
    PIXI.loader.resources["car2.png"].texture
  );
  car.y = 600 - car.height;

  for (var i = 0; i < 3; i++) {
    var lane;
    lane = new PIXI.Container();
    lane.gutter = 20;
    lane.vy = -2;
    lane.x = 40 + i * 110;
    for (var y = -(car.height + lane.gutter); y < (600 + car.height); y += (car.height + lane.gutter)) {
      var c = new PIXI.Sprite(
        PIXI.loader.resources["car.png"].texture
      );
      c.y = y;
      lane.addChild(c);
    }
    lanes[i] = lane;
    stage.addChild(lane);
  }

  //Capture the keyboard arrow keys
  var left = keyboard(37);
  var right = keyboard(39);

  //Left arrow key `press` method
  left.press = function() {
    if (laneNumber> 0) {
      laneNumber--;
    }
  };

  //Right
  right.press = function() {
    if (laneNumber < 2) {
      laneNumber++;
    }
  };

  message = new PIXI.Text(
    "Hello Pixi!",
    {fontFamily: "Arial", fontSize: 32, fill: "red"}
  );
  message.position.set(360, 96);
  stage.addChild(message);
  stage.addChild(car);

  //Set the game state
  state = play;

  gameLoop();
}

function gameLoop() {

  //Loop this function at 60 frames per second
  requestAnimationFrame(gameLoop);

  //Update the current game state:
  state();

  //Render the stage to see the animation
  renderer.render(stage);
}

function play() {
  car.x = 40 + laneNumber * 110;

  road.y += road.vy;
  if (road.y > 120) {
    road.y = 0;
  }

  var dt = Date.now();
  if (dt - lastUpdate > 3000) {
    lastUpdate = dt;
    for (var i = 0, len = lanes.length; i < len; i++) {
      lanes[i].vy = randomInt(-4, 2);
    }
  }

  for (var i = 0, len = lanes.length; i < len; i++) {
    if (laneNumber != i) {
      lanes[i].y += lanes[i].vy;
    }
    if (lanes[i].y < -(car.height + lanes[i].gutter) || lanes[i].y > (car.height + lanes[i].gutter)) {
      lanes[i].y = 0;
    }
  }

  message.text = laneNumber;
}

function keyboard(keyCode) {
  var key = {};
  key.code = keyCode;
  key.isDown = false;
  key.isUp = true;
  key.press = undefined;
  key.release = undefined;
  //The `downHandler`
  key.downHandler = function(event) {
    if (event.keyCode === key.code) {
      if (key.isUp && key.press) key.press();
      key.isDown = true;
      key.isUp = false;
    }
    event.preventDefault();
  };

  //The `upHandler`
  key.upHandler = function(event) {
    if (event.keyCode === key.code) {
      if (key.isDown && key.release) key.release();
      key.isDown = false;
      key.isUp = true;
    }
    event.preventDefault();
  };

  //Attach event listeners
  window.addEventListener(
    "keydown", key.downHandler.bind(key), false
  );
  window.addEventListener(
    "keyup", key.upHandler.bind(key), false
  );
  return key;
}

//The `randomInt` helper function
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
