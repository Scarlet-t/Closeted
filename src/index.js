import Phaser from 'phaser';

var config = {
    type: Phaser.AUTO,
    parent: 'game-body',
    width: 1404,
    height: 2496,
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        min: {
            width: 480,
            height: 270
        },
        max: {
            width: 1404,
            height: 2496
        },

        zoom: 1

    },
    autoRound: false,
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

var game = new Phaser.Game(config);

// to do
// 1. get icons into game
// 2. group em and somehow make em all swipable
// 3. write a function that turns all outfit images into appropriately sized icons that load in whenever the appropriate icon is pressed


function preload ()
{
    this.load.pack('asset_pack', 'assets.json');
}

function create ()
{
    this.add.image(0, 0, 'frame.1').setOrigin(0, 0);
}

function update ()
{
}
