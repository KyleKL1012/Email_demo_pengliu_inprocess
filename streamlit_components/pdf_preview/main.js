// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.
//
// If absolute URL from the remote server is provided, configure the CORS
// header on that server.
//
//
// In cases when the pdf.worker.js is located at the different folder than the
// PDF.js's one, or the PDF.js is executed via eval(), the workerSrc property
// shall be specified.
//
pdfjsLib.GlobalWorkerOptions.workerSrc =
  './node_modules/pdfjs-dist/build/pdf.worker.js';

var pdfDoc = null,
  pageNum = 1,
  pageRendering = false,
  pageNumPending = null,
  scale = 0.8,
  canvas = document.getElementById('pdf-canvas'),
  ctx = canvas.getContext('2d');

/**
 * Get page info from document, resize canvas accordingly, and render page.
 * @param num Page number.
 */
function renderPage(num) {
  pageRendering = true;
  // Using promise to fetch the page
  pdfDoc.getPage(num).then(function (page) {
    var viewport = page.getViewport({ scale: scale, });
    // Support HiDPI-screens.
    var outputScale = window.devicePixelRatio || 1;

    canvas.width = Math.floor(viewport.width * outputScale);
    canvas.height = Math.floor(viewport.height * outputScale);
    canvas.style.width = Math.floor(viewport.width) + "px";
    canvas.style.height = Math.floor(viewport.height) + "px";

    var transform = outputScale !== 1
      ? [outputScale, 0, 0, outputScale, 0, 0]
      : null;

    // Render PDF page into canvas context
    var renderContext = {
      canvasContext: ctx,
      transform: transform,
      viewport: viewport,
    };

    var renderTask = page.render(renderContext);

    // Wait for rendering to finish
    renderTask.promise.then(function () {
      pageRendering = false;
      if (pageNumPending !== null) {
        // New page rendering is pending
        renderPage(pageNumPending);
        pageNumPending = null;
      }
    });
  });

  // Update page counters
  document.getElementById('page_num').textContent = num;
}

/**
 * If another page rendering in progress, waits until the rendering is
 * finished. Otherwise, executes rendering immediately.
 */
function queueRenderPage(num) {
  if (pageRendering) {
    pageNumPending = num;
  } else {
    renderPage(num);
  }
}

/**
 * Displays previous page.
 */
function onPrevPage() {
  if (pageNum <= 1) {
    return;
  }
  pageNum--;
  queueRenderPage(pageNum);
}
document.getElementById('prev').addEventListener('click', onPrevPage);

/**
 * Displays next page.
 */
function onNextPage() {
  if (pageNum >= pdfDoc.numPages) {
    return;
  }
  pageNum++;
  queueRenderPage(pageNum);
}
document.getElementById('next').addEventListener('click', onNextPage);


function sendValue(value) {
  Streamlit.setComponentValue(value)
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event) {
  // Only run the render code the first time the component is loaded.
  // if (!window.rendered) {
  //   // You most likely want to get the data passed in like this
  //   // const {input1, input2, input3} = event.detail.args

  //   // You'll most likely want to pass some data back to Python like this
  //   // sendValue({output1: "foo", output2: "bar"})
  //   window.rendered = true
  // }
  const { src, page } = event.detail.args;
  /**
   * Asynchronously downloads PDF.
   */
  var pdfData = atob(src)
  var loadingTask = pdfjsLib.getDocument({ data: pdfData, });;
  pageNum = page
  loadingTask.promise.then(function (pdfDoc_) {
    pdfDoc = pdfDoc_;
    document.getElementById('page_count').textContent = pdfDoc.numPages;
    // Initial/first page rendering
    renderPage(pageNum);
  });
  // const canvas = document.getElementById("pdf-canvas")
  // pdfjsLib.getDocument(src+page).promise.then(function(pdfDoc) {
  //   pdfDoc.getPage(1).then(function(page) {
  //     const viewport = page.getViewport({scale: 1});
  //     const context = canvas.getContext('2d');
  //     canvas.height = viewport.height;
  //     canvas.width = viewport.width;

  //     page.render({
  //       canvasContext: context,
  //       viewport: viewport
  //     });
  //   });
  // });

  // Set the label text to be what the user specified
  // const pdfPreview = document.getElementById("pdf-preview")
  // var clone = pdfPreview.cloneNode(true);
  // clone.setAttribute('data', src+page);
  // console.log('pdfBase64',src+page)
  // pdfPreview.parentNode.replaceChild(clone, pdfPreview)
  // sendValue(1)

}

// Render the component whenever python send a "render event"
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
// Tell Streamlit that the component is ready to receive events
Streamlit.setComponentReady()
// Render with the correct height, if this is a fixed-height component
Streamlit.setFrameHeight(600)
// function accountNumberResponseHandler(event) {
//   const { element } = event.data;

//   const button = document.createElement('button');
//   button.type = 'button';
//   button.innerHTML = 'Fill in account number';
//   button.addEventListener('click', () => {
//     // Look for the account number element in the document and fill in the account number. You could get this value
//     // from a context variable in the message.
//     document.querySelector('#account-number').value = '1234567';
//   });

//   const container = document.createElement('div');
//   // This class name will allow our button to look like the default buttons used in web chat.
//   container.classList.add('ibm-web-chat--default-styles');
//   container.appendChild(button);

//   element.appendChild(container);
// }

/**
 * This will look for the "fill_phone_number" user defined value and if it sees it, will fill in the phone form
 * field.
 */

