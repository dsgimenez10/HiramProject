// BLOQUE 1 – Variables globales y selección de elementos del DOM 
// Elementos del formulario y del SVG del Yeti
var emailLabel = document.querySelector('#loginEmailLabel'),
    email = document.querySelector('#loginEmail'),
    passwordLabel = document.querySelector('#loginPasswordLabel'),
    password = document.querySelector('#loginPassword'),
    showPasswordCheck = document.querySelector('#showPasswordCheck'),
    showPasswordToggle = document.querySelector('#showPasswordToggle'),
    mySVG = document.querySelector('.svgContainer'),
    twoFingers = document.querySelector('.twoFingers'),
    armL = document.querySelector('.armL'),
    armR = document.querySelector('.armR'),
    eyeL = document.querySelector('.eyeL'),
    eyeR = document.querySelector('.eyeR'),
    nose = document.querySelector('.nose'),
    mouth = document.querySelector('.mouth'),
    mouthBG = document.querySelector('.mouthBG'),
    mouthSmallBG = document.querySelector('.mouthSmallBG'),
    mouthMediumBG = document.querySelector('.mouthMediumBG'),
    mouthLargeBG = document.querySelector('.mouthLargeBG'),
    mouthMaskPath = document.querySelector('#mouthMaskPath'),
    mouthOutline = document.querySelector('.mouthOutline'),
    tooth = document.querySelector('.tooth'),
    tongue = document.querySelector('.tongue'),
    chin = document.querySelector('.chin'),
    face = document.querySelector('.face'),
    eyebrow = document.querySelector('.eyebrow'),
    outerEarL = document.querySelector('.earL .outerEar'),
    outerEarR = document.querySelector('.earR .outerEar'),
    earHairL = document.querySelector('.earL .earHair'),
    earHairR = document.querySelector('.earR .earHair'),
    hair = document.querySelector('.hair'),
    bodyBG = document.querySelector('.bodyBGnormal'),
    bodyBGchanged = document.querySelector('.bodyBGchanged');

// Variables de estado y coordenadas usadas para animación
var activeElement, curEmailIndex, screenCenter, svgCoords, emailCoords, emailScrollMax;
var chinMin = .5, dFromC, mouthStatus = "small", blinking, eyeScale = 1;
var eyesCovered = false, showPasswordClicked = false;
var eyeLCoords, eyeRCoords, noseCoords, mouthCoords;
var eyeLAngle, eyeLX, eyeLY, eyeRAngle, eyeRX, eyeRY;
var noseAngle, noseX, noseY, mouthAngle, mouthX, mouthY, mouthR;
var chinX, chinY, chinS, faceX, faceY, faceSkew;
var eyebrowSkew, outerEarX, outerEarY, hairX, hairS;

// BLOQUE 2 – Movimiento facial en base al caret en el email
function calculateFaceMove(e) {
    // Crea un div temporal para obtener la posición del cursor (caret) en el campo email
    var carPos = email.selectionEnd,
        div = document.createElement('div'),
        span = document.createElement('span'),
        copyStyle = getComputedStyle(email),
        caretCoords = {};

    if (carPos == null || carPos == 0) carPos = email.value.length;

    // Copia estilos del input al div para simular la posición real del caret
    [].forEach.call(copyStyle, function(prop) {
        div.style[prop] = copyStyle[prop];
    });

    div.style.position = 'absolute';
    document.body.appendChild(div);
    div.textContent = email.value.substr(0, carPos);
    span.textContent = email.value.substr(carPos) || '.';
    div.appendChild(span);

    // Calcula los ángulos desde cada parte del Yeti hacia el caret
    if (email.scrollWidth <= emailScrollMax) {
        caretCoords = getPosition(span);
        dFromC = screenCenter - (caretCoords.x + emailCoords.x);
        eyeLAngle = getAngle(eyeLCoords.x, eyeLCoords.y, emailCoords.x + caretCoords.x, emailCoords.y + 25);
        eyeRAngle = getAngle(eyeRCoords.x, eyeRCoords.y, emailCoords.x + caretCoords.x, emailCoords.y + 25);
        noseAngle = getAngle(noseCoords.x, noseCoords.y, emailCoords.x + caretCoords.x, emailCoords.y + 25);
        mouthAngle = getAngle(mouthCoords.x, mouthCoords.y, emailCoords.x + caretCoords.x, emailCoords.y + 25);
    } else {
        // Si el input hace scroll horizontal, mira hacia el extremo derecho
        eyeLAngle = getAngle(eyeLCoords.x, eyeLCoords.y, emailCoords.x + emailScrollMax, emailCoords.y + 25);
        eyeRAngle = getAngle(eyeRCoords.x, eyeRCoords.y, emailCoords.x + emailScrollMax, emailCoords.y + 25);
        noseAngle = getAngle(noseCoords.x, noseCoords.y, emailCoords.x + emailScrollMax, emailCoords.y + 25);
        mouthAngle = getAngle(mouthCoords.x, mouthCoords.y, emailCoords.x + emailScrollMax, emailCoords.y + 25);
    }

    // Convierte los ángulos en desplazamientos (ejes X/Y)
    eyeLX = Math.cos(eyeLAngle) * 20;
    eyeLY = Math.sin(eyeLAngle) * 10;
    eyeRX = Math.cos(eyeRAngle) * 20;
    eyeRY = Math.sin(eyeRAngle) * 10;
    noseX = Math.cos(noseAngle) * 23;
    noseY = Math.sin(noseAngle) * 10;
    mouthX = Math.cos(mouthAngle) * 23;
    mouthY = Math.sin(mouthAngle) * 10;
    mouthR = Math.cos(mouthAngle) * 6;
    chinX = mouthX * .8;
    chinY = mouthY * .5;
    chinS = 1 - ((dFromC * .15) / 100);
    if (chinS > 1) {
        chinS = 1 - (chinS - 1);
        if (chinS < chinMin) chinS = chinMin;
    }

    // Aplica escala y rotación a otros elementos del rostro
    faceX = mouthX * .3;
    faceY = mouthY * .4;
    faceSkew = Math.cos(mouthAngle) * 5;
    eyebrowSkew = Math.cos(mouthAngle) * 25;
    outerEarX = Math.cos(mouthAngle) * 4;
    outerEarY = Math.cos(mouthAngle) * 5;
    hairX = Math.cos(mouthAngle) * 6;
    hairS = 1.2;

    // Animaciones GSAP para mover cada parte del SVG
    TweenMax.to(eyeL, 1, {x: -eyeLX, y: -eyeLY, ease: Expo.easeOut});
    TweenMax.to(eyeR, 1, {x: -eyeRX, y: -eyeRY, ease: Expo.easeOut});
    TweenMax.to(nose, 1, {x: -noseX, y: -noseY, rotation: mouthR, transformOrigin: "center center", ease: Expo.easeOut});
    TweenMax.to(mouth, 1, {x: -mouthX, y: -mouthY, rotation: mouthR, transformOrigin: "center center", ease: Expo.easeOut});
    TweenMax.to(chin, 1, {x: -chinX, y: -chinY, scaleY: chinS, ease: Expo.easeOut});
    TweenMax.to(face, 1, {x: -faceX, y: -faceY, skewX: -faceSkew, transformOrigin: "center top", ease: Expo.easeOut});
    TweenMax.to(eyebrow, 1, {x: -faceX, y: -faceY, skewX: -eyebrowSkew, transformOrigin: "center top", ease: Expo.easeOut});
    TweenMax.to(outerEarL, 1, {x: outerEarX, y: -outerEarY, ease: Expo.easeOut});
    TweenMax.to(outerEarR, 1, {x: outerEarX, y: outerEarY, ease: Expo.easeOut});
    TweenMax.to(earHairL, 1, {x: -outerEarX, y: -outerEarY, ease: Expo.easeOut});
    TweenMax.to(earHairR, 1, {x: -outerEarX, y: outerEarY, ease: Expo.easeOut});
    TweenMax.to(hair, 1, {x: hairX, scaleY: hairS, transformOrigin: "center bottom", ease: Expo.easeOut});

    // Limpia el div auxiliar creado
    document.body.removeChild(div);
}

// BLOQUE 3 – Reacción del Yeti al escribir en el campo de email
function showMouth(size) {
  mouthSmallBG.style.display = 'none';
  mouthMediumBG.style.display = 'none';
  mouthLargeBG.style.display = 'none';

  if (size === 'small') {
    mouthSmallBG.style.display = 'block';
  } else if (size === 'medium') {
    mouthMediumBG.style.display = 'block';
  } else if (size === 'large') {
    mouthLargeBG.style.display = 'block';
  }
}


function onEmailInput(e) {
	calculateFaceMove(e);
	var value = email.value;
	curEmailIndex = value.length;
  
	if (curEmailIndex > 0) {
	  // Siempre que hay texto, mostrar boca grande
	  mouthStatus = "large";
	  showMouth('large');
  
	  TweenMax.to(tooth, 1, { x: 3, y: -2, ease: Expo.easeOut });
	  TweenMax.to(tongue, 1, { y: 2, ease: Expo.easeOut });
	  TweenMax.to([eyeL, eyeR], 1, {
		scaleX: 0.65,
		scaleY: 0.65,
		transformOrigin: "center center",
		ease: Expo.easeOut
	  });
	  eyeScale = 0.65;
	} else {
	  // Si no hay texto, vuelve a la boca pequeña
	  mouthStatus = "small";
	  showMouth('small');
  
	  TweenMax.to(tooth, 1, { x: 0, y: 0, ease: Expo.easeOut });
	  TweenMax.to(tongue, 1, { y: 0, ease: Expo.easeOut });
	  TweenMax.to([eyeL, eyeR], 1, { scaleX: 1, scaleY: 1, ease: Expo.easeOut });
	  eyeScale = 1;
	}
  }

// BLOQUE 4 – Eventos del campo email
function onEmailFocus(e) {
    activeElement = "email";
    e.target.parentElement.classList.add("focusWithText"); // estilo visual para mostrar que está enfocado
    onEmailInput(); // actualiza expresión del Yeti al ingresar al campo
}

function onEmailBlur(e) {
    activeElement = null;
    setTimeout(function () {
        // Si no está activo y el campo está vacío, quita clase visual
        if (activeElement !== "email") {
            if (e.target.value === "") {
                e.target.parentElement.classList.remove("focusWithText");
            }
            resetFace(); // vuelve la cara del Yeti a su forma neutral
        }
    }, 100);
}

function onEmailLabelClick(e) {
    // Activa la lógica si se hace click en la etiqueta del input
    activeElement = "email";
}

// BLOQUE 5 – Eventos del campo contraseña

function onPasswordFocus(e) {
    activeElement = "password";
    if (!eyesCovered) {
        coverEyes(); // El Yeti se cubre los ojos
    }
}

function onPasswordBlur(e) {
    activeElement = null;
    setTimeout(function () {
        if (activeElement !== "password" && activeElement !== "toggle") {
            uncoverEyes(); // El Yeti deja de cubrirse si no está en el input ni en el toggle
        }
    }, 100);
}

// BLOQUE 6 – Mostrar/Ocultar contraseña
function onPasswordToggleFocus(e) {
    activeElement = "toggle";
    if (!eyesCovered) {
        coverEyes();
    }
}

function onPasswordToggleBlur(e) {
    activeElement = null;
    if (!showPasswordClicked) {
        setTimeout(function () {
            if (activeElement !== "password" && activeElement !== "toggle") {
                uncoverEyes();
            }
        }, 100);
    }
}

function onPasswordToggleMouseDown(e) {
    showPasswordClicked = true;
}

function onPasswordToggleMouseUp(e) {
    showPasswordClicked = false;
}

function onPasswordToggleChange(e) {
    // Cambia el tipo de input para mostrar u ocultar la contraseña
    setTimeout(function () {
        if (e.target.checked) {
            password.type = "text";
            spreadFingers(); // mueve los dedos del Yeti
        } else {
            password.type = "password";
            closeFingers();
        }
    }, 100);
}

function onPasswordToggleClick(e) {
    e.target.focus();
}

// BLOQUE 7 – Movimiento de dedos y brazos
function spreadFingers() {
    // Separa los dedos del Yeti (cuando se muestra la contraseña)
    TweenMax.to(twoFingers, 0.35, {
        transformOrigin: "bottom left",
        rotation: 30,
        x: -9,
        y: -2,
        ease: Power2.easeInOut
    });
}

function closeFingers() {
    // Vuelve los dedos a su posición original
    TweenMax.to(twoFingers, 0.35, {
        transformOrigin: "bottom left",
        rotation: 0,
        x: 0,
        y: 0,
        ease: Power2.easeInOut
    });
}

function coverEyes() {
    // El Yeti se cubre los ojos (brazos suben al rostro)
    TweenMax.killTweensOf([armL, armR]);
    TweenMax.set([armL, armR], { visibility: "visible" });

    TweenMax.to(armL, 0.45, { x: -93, y: 10, rotation: 0, ease: Quad.easeOut });
    TweenMax.to(armR, 0.45, {
        x: -93,
        y: 10,
        rotation: 0,
        delay: 0.1,
        ease: Quad.easeOut
    });

    bodyBG.style.display = "none";
	bodyBGchanged.style.display = "block";
    eyesCovered = true;
}

function uncoverEyes() {
    // El Yeti baja los brazos (deja de cubrirse)
    TweenMax.killTweensOf([armL, armR]);

    TweenMax.to(armL, 1.35, { y: 220, ease: Quad.easeOut });
    TweenMax.to(armL, 1.35, {
        rotation: 105,
        delay: 0.1,
        ease: Quad.easeOut
    });

    TweenMax.to(armR, 1.35, { y: 220, ease: Quad.easeOut });
    TweenMax.to(armR, 1.35, {
        rotation: -105,
        delay: 0.1,
        ease: Quad.easeOut,
        onComplete: function () {
            TweenMax.set([armL, armR], { visibility: "hidden" });
        }
    });

    bodyBGchanged.style.display = "none";
	bodyBG.style.display = "block";
    eyesCovered = false;
}

// BLOQUE 8 – Restaurar cara a estado neutral
function resetFace() {
    // Reinicia la cara del Yeti a su estado original (neutro)
    TweenMax.to([eyeL, eyeR], 1, { x: 0, y: 0, ease: Expo.easeOut });
    TweenMax.to(nose, 1, { x: 0, y: 0, scaleX: 1, scaleY: 1, ease: Expo.easeOut });
    TweenMax.to(mouth, 1, { x: 0, y: 0, rotation: 0, ease: Expo.easeOut });
    TweenMax.to(chin, 1, { x: 0, y: 0, scaleY: 1, ease: Expo.easeOut });
    TweenMax.to([face, eyebrow], 1, { x: 0, y: 0, skewX: 0, ease: Expo.easeOut });
    TweenMax.to([outerEarL, outerEarR, earHairL, earHairR, hair], 1, {
        x: 0,
        y: 0,
        scaleY: 1,
        ease: Expo.easeOut
    });
}

// BLOQUE 9 – Parpadeo automático del Yeti
function startBlinking(delay) {
    // Inicia parpadeo automático con un delay aleatorio
    if (delay) {
        delay = getRandomInt(delay);
    } else {
        delay = 1;
    }

    blinking = TweenMax.to([eyeL, eyeR], 0.1, {
        delay: delay,
        scaleY: 0,
        yoyo: true,
        repeat: 1,
        transformOrigin: "center center",
        onComplete: function () {
            startBlinking(12); // vuelve a llamar para continuar parpadeando
        }
    });
}

function stopBlinking() {
    // Detiene el parpadeo
    blinking.kill();
    blinking = null;
    TweenMax.set([eyeL, eyeR], { scaleY: eyeScale });
}

// BLOQUE 10 – Funciones utilitarias
function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}

function getAngle(x1, y1, x2, y2) {
    // Retorna el ángulo entre dos coordenadas
    return Math.atan2(y1 - y2, x1 - x2);
}

function getPosition(el) {
    // Calcula la posición absoluta de un elemento en pantalla
    var xPos = 0, yPos = 0;

    while (el) {
        if (el.tagName == "BODY") {
            var xScroll = el.scrollLeft || document.documentElement.scrollLeft;
            var yScroll = el.scrollTop || document.documentElement.scrollTop;

            xPos += (el.offsetLeft - xScroll + el.clientLeft);
            yPos += (el.offsetTop - yScroll + el.clientTop);
        } else {
            xPos += (el.offsetLeft - el.scrollLeft + el.clientLeft);
            yPos += (el.offsetTop - el.scrollTop + el.clientTop);
        }

        el = el.offsetParent;
    }

    return { x: xPos, y: yPos };
}

function isMobileDevice() {
    // Detecta si el usuario está en un dispositivo móvil
    var check = false;
    (function (a) {
        if (/android|iphone|ipad|mobile/i.test(a)) check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    return check;
}

// BLOQUE 11 – Inicialización principal del formulario
function initLoginForm() {
    // Obtiene posiciones iniciales de los elementos SVG
    svgCoords = getPosition(mySVG);
    emailCoords = getPosition(email);
    screenCenter = svgCoords.x + (mySVG.offsetWidth / 2);

    // Coordenadas fijas para los ojos, nariz y boca del Yeti
    eyeLCoords = { x: svgCoords.x + 84, y: svgCoords.y + 76 };
    eyeRCoords = { x: svgCoords.x + 113, y: svgCoords.y + 76 };
    noseCoords = { x: svgCoords.x + 97, y: svgCoords.y + 81 };
    mouthCoords = { x: svgCoords.x + 100, y: svgCoords.y + 100 };

    // Eventos de email
    email.addEventListener('focus', onEmailFocus);
    email.addEventListener('blur', onEmailBlur);
    email.addEventListener('input', onEmailInput);
    emailLabel.addEventListener('click', onEmailLabelClick);

    // Eventos de contraseña
    password.addEventListener('focus', onPasswordFocus);
    password.addEventListener('blur', onPasswordBlur);

    // Checkbox mostrar contraseña
    showPasswordCheck.addEventListener('change', onPasswordToggleChange);
    showPasswordCheck.addEventListener('focus', onPasswordToggleFocus);
    showPasswordCheck.addEventListener('blur', onPasswordToggleBlur);
    showPasswordCheck.addEventListener('click', onPasswordToggleClick);
    showPasswordToggle.addEventListener('mouseup', onPasswordToggleMouseUp);
    showPasswordToggle.addEventListener('mousedown', onPasswordToggleMouseDown);

    // Posición inicial de los brazos
    TweenMax.set(armL, { x: -93, y: 220, rotation: 105, transformOrigin: "top left" });
    TweenMax.set(armR, { x: -93, y: 220, rotation: -105, transformOrigin: "top right" });

    // Fija el punto de transformación de la boca
    TweenMax.set(mouth, { transformOrigin: "center center" });

    // Activa el parpadeo
    startBlinking(5);

    // Determina el punto máximo de scroll del input
    emailScrollMax = email.scrollWidth;

    // Si es un móvil, mostrar contraseña por defecto
    if (isMobileDevice()) {
        password.type = "text";
        showPasswordCheck.checked = true;
        TweenMax.set(twoFingers, {
            transformOrigin: "bottom left",
            rotation: 30,
            x: -9,
            y: -2,
            ease: Power2.easeInOut
        });
    }

    // Mostrar estado inicial con boca "small", diente y lengua visibles
    mouthStatus = "small";

    // Asegura que solo se muestre la boca chica
    mouthBG.style.display = 'none';
    mouthSmallBG.style.display = 'block';
    mouthMediumBG.style.display = 'none';
    mouthLargeBG.style.display = 'none';

    // Mostrar diente y lengua
    if (tooth) tooth.style.display = 'block';
    if (tongue) tongue.style.display = 'block';

    // Limpia consola
    console.clear();
}



// Llama a la función principal de arranque
initLoginForm();
