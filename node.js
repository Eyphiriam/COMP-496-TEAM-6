// Install required modules: express, multer
const express = require('express');
const multer = require('multer');
const path = require('path');
const app = express();

// Set storage engine
const storage = multer.diskStorage({
    destination: './uploads/',
    filename: function(req, file, cb) {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
    }
});

// Init upload
const upload = multer({
    storage: storage,
    limits: { fileSize: 5000000 }, // 5MB limit
    fileFilter: function(req, file, cb) {
        checkFileType(file, cb);
    }
}).single('image');

// Check file type
function checkFileType(file, cb) {
    const filetypes = /jpeg|jpg|png|gif/;
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = filetypes.test(file.mimetype);

    if (mimetype && extname) {
        return cb(null, true);
    } else {
        cb('Error: Images Only!');
    }
}

app.use(express.static('./public'));

// Upload route
app.post('/upload', (req, res) => {
    upload(req, res, (err) => {
        if (err) {
            res.status(400).send({ message: err });
        } else {
            if (req.file == undefined) {
                res.status(400).send({ message: 'No file selected!' });
            } else {
                res.send({
                    message: 'File uploaded successfully!',
                    file: `uploads/${req.file.filename}`
                });
            }
        }
    });
});

app.listen(3000, () => {
    console.log('Server started on port 3000');
});