require.undef('signals');
define('signals', ['d3'], function (d3) {
  const width  = 1000;
  const height = 300;
  const pad = {l: 30, t: 10};

  function draw_hist(svg, data) {
    const h = svg.append('g');

    h.append('line')
      .attr('stroke', 'currentColor')
      .attr('x1', width-pad.t + 0.5).attr('x2', width-pad.t + 0.5)
      .attr('y1', pad.t).attr('y2', height - pad.l);

    h.append('line')
      .attr('stroke', 'currentColor')
      .attr('x1', pad.l).attr('x2', width - pad.t)
      .attr('y1', pad.t + 0.5).attr('y2', pad.t + 0.5);

    let xL = Infinity, xR = -Infinity, yM = 0;
    let D = data.map((one) => {
      let Xs = one[1], Ys = one[0];
      let d = [{x: Xs[0], y: 0}];
      Xs.slice(1).map((x, k) => d.push({x: (Xs[k + 1] + Xs[k])/2, y: Ys[k]}));
      d.push({x: Xs[Xs.length - 1], y: 0});
      xL = d3.min([d3.min(Xs), xL]);
      xR = d3.max([d3.max(Xs), xR]);
      yM = d3.max([d3.max(Ys), yM]);
      return d;
    });

    let x = d3.scaleLinear()
      .range([0, width - pad.l - pad.t])
      .domain([xL, xR]);
    let axisX = d3.axisBottom(x);

    let y = d3.scaleLinear()
      .range([height - pad.l - pad.t, 0])
      .domain([0, yM]);
    let axisY = d3.axisLeft(y).ticks(5);
    
    h.append('g')
      .attr('transform', `translate(${pad.l}, ${height-pad.l})`)
      .call(axisX);

    h.append('g')
      .attr('transform', `translate(${pad.l}, ${pad.t})`)
      .call(axisY);

    D.map((T, col) => {
      let line = d3.line().x(d => x(d.x)).y(d => y(d.y));
      h.append('path')
        .datum(T)
        .attr('class', 'hist-line')
        .attr('fill', colors(col))
        .attr('transform', `translate(${pad.l}, ${pad.t})`)
        .attr('d', line);
    });
    
    return {h, x, y};
  }
  
  function getRandomSubarray(arr, size) {
    var shuffled = arr.slice(0), i = arr.length, temp, index;
    while (i--) {
        index = Math.floor((i + 1) * Math.random());
        temp = shuffled[index];
        shuffled[index] = shuffled[i];
        shuffled[i] = temp;
    }
    return shuffled.slice(0, size);
  }

  function OLD(container, B, G, data) {
    let svg = d3.select(container)
      .append('svg')
      .attr('width',  3 * width + 20)
      .attr('height', height);

    let h = draw_hist(svg, data);

    let brush = d3.brushX()
      .extent([[0, 0], [width - pad.l - pad.t - 1.5, height - pad.l - pad.t - 1.5]])
      .on('brush end', brushed);

    let brushNode = h.h.append('g')
      .attr('transform', `translate(${pad.l + 1}, ${pad.t + 1.5})`)
      .attr('class', 'brush')
      .call(brush);

    let timer = null;
    function brushed() {
      let px = d3.event.selection || h.x.range();
      let bp = px.map(e => h.x.invert(e));
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        
        console.log(B);
        console.log(bp);
        let bb = B.filter(l => l[3] >= bp[0] && l[3] <= bp[1]);
        let gg = G.filter(l => l[3] >= bp[0] && l[3] <= bp[1]);
        
        h.h.selectAll('.coverage-box').remove();
        
        let c_b = svg.append('g')
          .attr('transform', `translate(${width + 20}, 0)`)
          .attr('class', 'coverage-box');
        let c_g = svg.append('g')
          .attr('transform', `translate(${2*(width + 20)}, 0)`)
          .attr('class', 'coverage-box');

        draw_cov_data(getRandomSubarray(bb, 70), c_b, colors(0));
        draw_cov_data(getRandomSubarray(gg, 70), c_g, colors(1));
      }, 500);
    }

    function draw_cov_data(ptx, c, color) {
      
      fetch('http://127.0.0.1:9950/depth/HG001', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ptx)
      })
      .then(res => res.json())
      .then(data => {
        if (data.length == 0) return;
        let MX = d3.mean(data.map(v => d3.mean(v))) * 2;

        let x_ = d3.scaleLinear()
          .range([0, width - pad.l - pad.t])
          .domain([0, data[0].length * 16]);

        let y_ = d3.scaleLinear()
          .range([height - pad.l - pad.t, 0])
          .domain([0, MX]);
        
        let axisX = d3.axisBottom(x_);
        let axisY = d3.axisLeft(y_).ticks(5);
        
        c.append('g')
          .attr('transform', `translate(${pad.l}, ${height-pad.l})`)
          .call(axisX);

        c.append('g')
          .attr('transform', `translate(${pad.l}, ${pad.t})`)
          .call(axisY);

        data.map((T, col) => {
          let line = d3.line().x(d => x_(d.x)).y(d => y_(d.y));
          c.append('path')
            .datum(T.map((v, k) => ({'y': v, 'x': k*16})))
            .attr('class', 'coverage-line')
            .attr('stroke', color)
            .attr('stroke-opacity', 2/data.length)
            .attr('transform', `translate(${pad.l}, ${pad.t})`)
            .attr('d', line);
        });
      });
    }
    console.log(container);
  }
});

require.undef('hists');
define('hists', ['d3'], function (d3) {
  const width  = 560;
  const height = 300;
  const pad = {l: 30, t: 10};

  function draw_hists(container, data) {
    const keys = Object.keys(data)
    //const scheme = d3.scaleOrdinal().domain(keys.length).range(d3.schemeSet1)
    let scheme = d3.scaleSequential().domain([keys.length + 1, 0]).interpolator(d3.interpolateTurbo);
    if (keys.length == 1) scheme = (n) => '#6e6eff';
    // console.log(keys);
    
    let svg = d3.select(container)
      .attr('class', 'hist-wrapper')
      .append('svg')
      .attr('style', 'overflow: visible')
      .attr('width',  width)
      .attr('height', height);

    // Frame:
    svg.append('line')
      .attr('stroke', 'currentColor')
      .attr('x1', width-pad.t + 0.5).attr('x2', width-pad.t + 0.5)
      .attr('y1', pad.t).attr('y2', height - pad.l);
    svg.append('line')
      .attr('stroke', 'currentColor')
      .attr('x1', pad.l).attr('x2', width - pad.t)
      .attr('y1', pad.t + 0.5).attr('y2', pad.t + 0.5);
    
    // Hist -> points:
    let xL = Infinity, xR = -Infinity, yM = 0;
    let D = keys.map(key => {
      let Xs = data[key].x.slice(1).map((x, k) => (x + data[key].x[k+1])/2);
      let d = [{x: Xs[0], y: 0}];
      Xs.map((x, k) => d.push({x: x, y: data[key].y[k]}));
      d.push({x: Xs[Xs.length - 1], y: 0});
      xL = d3.min([d3.min(Xs), xL]);
      xR = d3.max([d3.max(Xs), xR]);
      yM = d3.max([d3.max(data[key].y), yM]);
      return d;
    });
    
    let x = d3.scaleLinear()
      .range([0, width - pad.l - pad.t])
      .domain([xL, xR]);
    let axisX = d3.axisBottom(x);
    svg.append('g')
      .attr('transform', `translate(${pad.l}, ${height-pad.l})`)
      .call(axisX);
    
    let y = d3.scaleLinear()
      .range([height - pad.l - pad.t, 0])
      .domain([0, yM]);
    let axisY = d3.axisLeft(y).ticks(5);
    svg.append('g')
      .attr('transform', `translate(${pad.l}, ${pad.t})`)
      .call(axisY);
    
    D.map((T, col) => {
      let line = d3.line().x(d => x(d.x)).y(d => y(d.y));
      svg.append('path')
        .datum(T)
        .attr('class', 'hist-line')
        .attr('fill', scheme(col+1))
        .attr('fill-opacity', keys.length > 1 ? 0.9/keys.length : 0.8)
        .attr('stroke', scheme(col+1))
        .attr('transform', `translate(${pad.l}, ${pad.t})`)
        .attr('d', line);
    });

    container.innerHTML += '<div class="legend">' + keys.map((key, i) => (
      `<div class="note"><span style="background: ${scheme(i+1)}"></span> ${key}</div>`
    )).join('') + '</div>';

  }
  
  return (function(cnt, data) {
    return draw_hists(cnt, data); 
  });
});

// element.append('<small>&#x25CB; Loaded hists.js &#x25CB;</small>');