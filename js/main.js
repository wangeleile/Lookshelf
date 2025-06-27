'use strict';

//get floor/ceiling range
function getRange(arr, by) {
  return [Math.floor(_.min(arr) / by) * by, Math.ceil(_.max(arr) / by) * by];
}

//calculate when to divide books
function getDivider(datum, option) {
  let val = datum[option];
  //get divider labels
  let label = val;
  if (option === 'year_desc') {
    label = -val;
  } else if (option === 'first_name' || option === 'last_name') {
    label = val.charAt(0);
  } else if (option === 'age_asc') {
    if (val > 0) {
      label = (Math.floor(Math.abs(val) / 10) * 10) + '+';
    } else if (val === 0) {
      label = 'Unknown';
    } else {
      label = 'After death';
    }
  } else if (option === 'age_desc') {
    if (val < 0) {
      label = (Math.floor(Math.abs(val) / 10) * 10) + '+';
    } else if (val === 0) {
      label = 'Unknown';
    } else {
      label = 'After death';
    }
  } else if (option === 'pages_asc' || option === 'pages_desc') {
    label = (Math.floor(Math.abs(val) / 100) * 100).toLocaleString() + '+';
  } else if (option === 'rating_asc' || option === 'rating_desc') {
    label = (Math.floor((Math.floor(Math.abs(val) * 10) * 2) / 10) / 2) + '+';
  } else if (option === 'rating_count_asc' || option === 'rating_count_desc') {
    label = Math.abs(val) < 10000 ? '<10K' : (Math.floor(Math.abs(val) / 10000) * 10000 / 1000 + 'K+');
  } else if (option === 'is_not_bestseller') {
    label = !val ? 'NYT Best seller' : 'Not Best Seller';
  } else if (option === 'is_english') {
    label = val ? 'English': 'Translated';
  } else if (option === 'title') {
    label = _.isNaN(+val.charAt(0)) ? val.charAt(0) : '#';
  } else if (option === 'title_desc' || option === 'title_asc') {
    label = (Math.floor(Math.abs(val) / 10) * 10).toLocaleString() + '+';
  }
  return label;
}

//draw stars
function starPoints(cX, cY, arms, oR, iR) {
  let results = '';
  const angle = Math.PI / arms;
  for (let i = 0; i < 2 * arms; i++) {
      var r = (i & 1) == 0 ? oR : iR;
      var currX = cX + Math.cos(i * angle) * r;
      var currY = cY + Math.sin(i * angle) * r;
      if (i == 0) {
        results = `${currX}, ${currY}`;
      } else {
        results += `, ${currX}, ${currY}`;
      }
   }
   return results;
}

//search
function getSearchedText(str, entered) {
  let result = str;
  const index = str.toLowerCase().indexOf(entered);
  if (index > -1) {
    result = `${str.substring(0, index)}<i>${str.substr(index, entered.length)}</i>${str.substring(index + entered.length, str.length)}`;
  }
  return result;
}

//show modal
function showModal(d, i, count, list, entered) {
  //control prev, next bottons
  d3.select('.js-modal-prev').classed('is-hidden', i <= 0);
  if (i > 0) {
    d3.select('.js-modal-prev').on('click', () => { showModal(list[i - 1], i - 1, count, list, entered) });
  }
  d3.select('.js-modal-next').classed('is-hidden', (i < count - 1 ? false : true));
  if (i < count - 1) {
    d3.select('.js-modal-next').on('click', () => { showModal(list[i + 1], i + 1, count, list, entered) });
  }
  d3.select('.js-d-genre').classed(`tag-${d.genre}`, true).classed(`tag-${d.genre === 'Fiction' ? 'Nonfiction' : 'Fiction'}`, false);
  d3.select('.js-modal-count').html(`${entered ? `Searched by <strong>${entered}</strong>, ` : ''}${i + 1}/${count}`);
  d3.select('.js-book-image').attr('src', d.image_url).attr('alt', d.title);
  d3.select('.js-d-title-link').attr('href', d.link || '#');
  let title = d.title.toUpperCase();
  let subtitle = 'N/A';
  const colon = d.title.indexOf(':');
  if (colon > -1) {
    title = d.title.slice(0, colon).toUpperCase();
    subtitle = d.title.slice(colon + 2, d.title.length);
  }
  const bookInfo = {
    title,
    subtitle,
    author: d.author,
    year: d.year,
    genre: d.genre,
    pages: d.pages,
    publication_date: d.publication_date,
    publisher: d.publisher,
    bestseller: d.bestseller ? 'Yes' : 'No',
    rating_avg: d.rating ? d.rating.toFixed(2) : 'N/A',
    rating_count: d.rating_count ? d.rating_count.toLocaleString() : 'N/A',
  };
  _.each(bookInfo, (v, k) => {
    if (v) {
      if (k === 'subtitle') {
        d3.select(`.js-d-${k}-wrapper`).classed('is-hidden', v === 'N/A');
      }
      d3.select(`.js-d-${k}`).html(v);
    }
  });
  d3.select('#modal-authors').html('');
}

function getShelfWidth() {
  return Math.max(document.getElementById('shelf').clientWidth, 700)
}
//put all javascript code in eine Funktion, die nach dem Laden von books.yaml aufgerufen wird
// Hilfsfunktion für Sortierung
function getSortParams(option) {
  switch(option) {
    case 'year_desc': return ['year', 'desc'];
    case 'year_asc': return ['year', 'asc'];
    case 'rating_desc': return ['rating', 'desc'];
    case 'rating_asc': return ['rating', 'asc'];
    default: return [option, 'asc'];
  }
}

function startApp(data) {
  // Nur eine Sortieroption (Standard: Jahr absteigend)
  let sortOption = 'year_desc';
  let [sortField, sortDir] = getSortParams(sortOption);
  let books = _.orderBy(data.books, [sortField], [sortDir]);

  //add text in headline
  d3.select('#headline-count').text(books.length);
  d3.select('#headline-year-start').text(_.minBy(books, 'year')?.year || '');
  d3.select('#headline-year-end').text(_.maxBy(books, 'year')?.year || '');
  d3.select('#generation-date').text(data.generation_date || '');

  //get wrapper width
  let divW = getShelfWidth();
  /* gap is drawn in svg, side are drawn in div style (background & border)
  =========== gap
  | story H |
  =========== gap
  | story H |
  =========== gap
  */
  //set range
  const storyH = 100; //same as maximum book height
  const storyGap = 40; //height of gap
  const bookWRange = [10, 60]; //book thickness
  const bookHRange = [60, storyH]; //book height range

  //put two Gs in the entire shelf, one for shelf bg, one for other elements
  const shelfG = d3.select('#shelf-svg').attr('width', divW).append('g');
  const g = d3.select('#shelf-svg').append('g');

  //dimensions für jedes Buch
  const pages = books.map((d) => d.pages);
  const pageRange = getRange(pages, 100);
  const ages = _.filter(books.map((d) => d.age_asc), (d) => d > 0);
  const ageRange = getRange(ages, 10);
  const bookW = d3.scaleLinear().domain(pageRange).range(bookWRange); //page
  const bookH = d3.scaleLinear().domain([3, 5]).range(bookHRange); //rating
  const middleH = d3.scaleLinear().domain(ageRange).range([10, bookHRange[0]]); //age

  //put legend of first level (id) and 2nd level
  const putLegend = (text, count, accW, accS, isInitial, gap) => {
    let triangle = 5;
    let pX = accW;
    let pY = (accS - 1) * (storyH + storyGap);
    let wrapper = g.append('g')
      .attr('transform', `translate(${pX}, ${pY})`)
      .attr('class', `js-legends${isInitial ? '' : ' is-hidden'}`)
    wrapper.append('rect')
      .attr('x', -gap + 5)
      .attr('y', storyGap)
      .attr('width', gap - 5.5)
      .attr('height', storyH)
      .attr('class', 'legend-0-bg');
    wrapper.append('text')
      .attr('x', -gap + 5)
      .attr('y', storyGap - triangle * 3)
      .attr('dy', -4)
      .text(text)
      .attr('class', 'legend-0');
    wrapper.append('text')
      .attr('x', -gap + 5 + triangle * 1.2 + 4)
      .attr('y', storyGap - triangle - 2)
      .attr('class', 'legend-0-count')
      .attr('id', `legend-0-${count}`);
    g.append('path')
      .attr('d', `M${pX - gap + 5} ${pY + storyGap - triangle * 2 - 2} l ${triangle * 1.2} ${triangle} l ${-triangle * 1.2} ${triangle} z`)
      .attr('class', `legend-arrow js-legends${isInitial ? '' : ' is-hidden'}`)
  };

  //sort options
  let sortOptions = ['year_desc', 'rating_desc', 'rating_asc', 'year_asc'];

  //get new positions for the books when option is changed & put legends
  function getDimensions(sortedBooks, isInitial) {
    //remove all legends first
    d3.selectAll('.js-legends').remove();
    d3.selectAll('.js-shelves').remove();
    let prevVal = getDivider(sortedBooks[0], sortOption);
    let edge = 10;
    let gap = 40;
    let accW = gap;
    let accS = 1;
    let dimensions = [];
    let count = 0;
    let isNewLabel = true;
    let labelCount = 0;
    _.each(sortedBooks, (d, i) => {
      const w = bookW(d.pages); //book width
      const h = bookH(d.rating); //book height
      const divider = getDivider(d, sortOption); //get labels at the dividing postions
      //check with the previous vals, then decide to divide or not
      if (divider !== prevVal) {
        accW += gap;
        isNewLabel = true;
      }
      //check if the accmulated books' width is larger than the shelf width
      if (accW + w > divW) {
        accS++;
        accW = gap;
      }
      //add dmensions
      dimensions.push({
        x: accW,
        y: (storyH + storyGap) * accS - h,
        bookId: d.id //needed for d3 selection
      })
      //update prev vals
      count++;
      //put the first level label
      if (isNewLabel) {
        putLegend(divider, labelCount, accW, accS, isInitial, gap);
        //update count for the previous values
        d3.select(`#legend-0-${labelCount - 1}`).text(count);
        count = 0;
        labelCount++;
      }
      //update the last labels; count
      if (i === sortedBooks.length - 1) {
        d3.select(`#legend-0-${labelCount - 1}`).text(count + 1);
      }
      //add width, update before the next iteration
      accW += (w + 0);
      prevVal = divider;
      isNewLabel = false;
    });

    //set the wrapper height to fit
    d3.select('#shelf-svg').attr('height', accS * (storyGap + storyH) + storyGap);
    // put story gap
    _.each(_.range(accS + 1), (i) => {
      shelfG.append('rect')
        .attr('x', 0)
        .attr('y', i * (storyH + storyGap))
        .attr('width', divW)
        .attr('height', storyGap)
        .attr('class', 'shelf-gap js-shelves')
    });
    return dimensions;
  }

  function resizeShelf() {
    [sortField, sortDir] = getSortParams(sortOption);
    books = _.orderBy(data.books, [sortField], [sortDir]);
    const dimensions = getDimensions(books, false);
    //disable the sorting options
    d3.selectAll('select').attr('disabled', 'disabled');
    //move books
    _.each(dimensions, (d, i) => {
      const bg = d3.select(`#book-${d.bookId}`);
      //move horizontally first, then move vertically
      const currentY = +bg.attr('prev-y');
      bg.attr('prev-y', d.y)
        .transition()
          .attr('transform', `translate(${d.x}, ${currentY})`)
          .duration(1000)
          .delay(800 * Math.random())
          .on('end', function() {
            d3.select(this)
              .transition()
              .duration(800)
              .delay(600 * Math.random())
              .attr('transform', `translate(${d.x}, ${d.y})`)
              .on('end', () => {
                //when animation ends, show the legends
                d3.selectAll('.js-legends').classed('is-hidden', false);
                //enable back the sorting options
                _.delay(() => { d3.selectAll('select').attr('disabled', null) }, 1400);
              });
          });
      bg.on('click', () => {
        d3.select('#modal').classed('is-active', true);
        showModal(books[i], i, dimensions.length, books);
      });
    });
  }

  // Sortierauswahl
  document.getElementById('sort-0').addEventListener('change', (d) => {
    sortOption = d.target.value;
    resizeShelf();
  });
  // Blende die zweite Sortieroption aus
  d3.select('#option-1').classed('is-hidden', true);

  /**********
  //draw book
  ***********/
  const dimensions = getDimensions(books, true);
  function getUpPos(elm, isUp) {
    //get current transform value, then update y pos
    const currP = elm.attr('transform');
    const splitted = currP.split(', ');
    const currY = splitted[1].slice(0, splitted[1].length - 1);
    return `${splitted[0]}, ${currY - (isUp ? 10 : -10)})`
  }
  g.selectAll('.js-books')
    .data(books)
      .enter()
    .append('g') //book wrapper
      .attr('transform', (d, i) => `translate(${dimensions[i].x}, ${dimensions[i].y})`)
      .attr('title', (d) => {
        let title = `<strong>${d.title.toUpperCase()}</strong>`;
        const colon = d.title.indexOf(':');
        if (colon > -1) {
          title = `<strong>${d.title.slice(0, colon).toUpperCase()}</strong><br/>${d.title.slice(colon + 2, d.title.length)}`
        }
        return `${title}<div><div class="author">by <strong>${d.author}</strong></div></div>`;
      })
      .attr('class', 'js-books')
      .attr('id', (d) => `book-${d.id}`)
      .attr('prev-y', (d, i) => dimensions[i].y)
      .on('mouseover', function(d) {
        if ('ontouchstart' in document) {
          return false;
        }
        //effect of book being picked up
        d3.select(`#book-${d.id}`)
          .attr('transform', getUpPos(d3.select(this), true));
        //tippy
        tippy(`#book-${d.id}`, {
          arrow: true,
          duration: 0,
          size: 'small',
          theme: `book-${d.genre}`
        });
      })
      .on('mouseout', function(d) {
        if ('ontouchstart' in document) {
          return false;
        }
        d3.select(`#book-${d.id}`)
          .attr('transform', getUpPos(d3.select(this), false));
      })
      .on('click', (d, i) => {
        d3.select('#modal').classed('is-active', true);
        showModal(d, i, books.length, books);
      })
    .append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', (d) => bookW(d.pages))
      .attr('height', (d) => bookH(d.rating))
      .attr('rx', 1)
      .attr('ry', 1)
      .attr('id', (d) => `book-rect-${d.id}`)
      .attr('class', (d) => `genre-${d.genre} book-${d.gender}`);
  //draw age overlay (optional, falls Feld vorhanden)
  // Bestseller und Sprache korrekt behandeln
  _.each(_.filter(books, (d) => d.bestseller), (d) => {
    d3.select(`#book-${d.id}`)
      .append('polygon')
      .attr('points', starPoints(
        bookW(d.pages) / 2,
        bookH(d.rating) - bookWRange[0] * 1.2,
        9,
        bookWRange[0] * 0.50,
        bookWRange[0] * 0.66
      ))
      .attr('class', 'bestseller')
  });
  _.each(_.filter(books, (d) => d.language && d.language !== 'English'), (d) => {
    d3.select(`#book-${d.id}`)
      .append('path')
      .attr('d', `M 0 0 h ${bookWRange[0]} l -${bookWRange[0]} ${bookWRange[0]} z`)
      .attr('class', 'translated')
  });
  //modal close
  d3.select('#modal-close').on('click', () => {
    d3.select('#modal').classed('is-active', false);
  })

  //search
  let selectedId = -1;
  function resetSearch() {
    selectedId = -1;
    d3.selectAll('.js-search-elm').classed('is-hidden', true);
    d3.select('#search-result').html('');
  }
  function triggerModal(obj, i, count, list, entered) {
    d3.select('#modal').classed('is-active', true);
    showModal(obj, i, count, list, entered);
    resetSearch();
  }
  document.getElementById('search-input').addEventListener('keyup', function(d) {
    //check from minimum 3 letters
    if (this.value.length > 2) {
      const entered = this.value.trim().toLowerCase();
      const filtered = _.filter(books, (d) => {
        return d.title.toLowerCase().indexOf(entered) > -1 ||
          d.author.toLowerCase().indexOf(entered) > -1 ||
          d.publisher.toLowerCase().indexOf(entered) > -1;
      });
      //show only books exists by the typed letters
      if (filtered.length > 0) {
        const bookIds = filtered.map((d) => d.book.id);
        const searched = filtered.map((d, i) => {
          let titleFormatted = d.title;
          const splitted = d.title.split(':')
          if (splitted.length > 1) {
            titleFormatted = `${splitted[0].toUpperCase()}:${splitted[1]}`;
          }
          let title = getSearchedText(titleFormatted, entered);
          let name = getSearchedText(d.author, entered);
          let publisher = getSearchedText(d.publisher, entered);
          return `<li class="item js-search-list js-search-${i}" search-id="${i}" id="search-${i}">${title}<br/>by ${name}, ${publisher}</li>`
        });
        //add list to <ul>
        d3.selectAll('.js-search-elm').classed('is-hidden', false);
        d3.select('#search-result')
          .html(`<li class="count" id="search-count"><i>${searched.length}</i> book${searched.length > 1 ? 's' : ''} found</a></li>${searched.join(' ')}`);
        //height of the count line
        const countH = document.getElementById('search-count').clientHeight;
        //down arrow pressed
        if (d.keyCode === 40) {
          selectedId = selectedId < searched.length - 1 ? selectedId + 1 : 0;
          //when getting back to the first item
          if (selectedId === 0) {
            document.getElementById('search-result').scrollTop = 0;
          } else {
            let prevH = countH;
            for (let i = 0; i <= selectedId; i++) {
              prevH += document.getElementById(`search-${i}`).clientHeight;
            }
            //30 is the height of <ul>, if it's bigger -> scroll
            if (prevH > 300) {
              document.getElementById('search-result').scrollTop = prevH - 300 + countH;
            }
          }
        //up arrow pressed
        } else if (d.keyCode === 38) {
          selectedId = selectedId > 0 ? selectedId - 1 : searched.length - 1;
          const scrollT = document.getElementById('search-result').scrollTop;
          let prevH = 0;
          for (let i = 0; i <= selectedId; i++) {
            prevH += document.getElementById(`search-${i}`).clientHeight;
          }
          //shen hitting the last item after loop
          if (selectedId === searched.length - 1) {
            document.getElementById('search-result').scrollTop = prevH;
          } else if (prevH < scrollT) {
            document.getElementById('search-result').scrollTop = prevH - 300 + countH;
          }
        //enter pressed
        } else if (d.keyCode === 13 && selectedId > -1) {
          triggerModal(filtered[selectedId], selectedId, filtered.length, filtered, entered);
          this.value = '';
        }
        d3.selectAll('.js-search-list').classed('item-hover', false);
        d3.select(`.js-search-${selectedId}`).classed('item-hover', true);
        //mouse interaction
        d3.selectAll('.js-search-list')
          .on('mouseover', function() {
            d3.select(this).classed('item-hover', true);
            selectedId = +d3.select(this).attr('search-id');
          })
          .on('mouseout', function() {
            d3.select(this).classed('item-hover', false);
          })
          .on('click', function() {
            let id = +d3.select(this).attr('search-id');
            triggerModal(filtered[id], id, filtered.length, filtered);
            document.getElementById('search-input').value = '';
          })
        d3.select('.js-search-close')
          .on('click', () => {
            this.value = '';
            resetSearch();
          });
      } else {
        resetSearch();
      }
    } else {
      resetSearch();
    }
  });

  //sort
  document.getElementById('sort-0').addEventListener('change', (d) => {
    sortOption = d.target.value;
    resizeShelf();
  });
  // Blende die zweite Sortieroption aus
  d3.select('#option-1').classed('is-hidden', true);

  //links
  d3.select('#links').on('click', () => {
    d3.select('.js-mobile-menu').classed('is-hidden', false);
  });
  d3.select('#links-close').on('click', () => {
    d3.select('.js-mobile-menu').classed('is-hidden', true);
  });

  //resize
  window.addEventListener('resize', _.debounce(() => {
    const newW = getShelfWidth();
    if (newW !== divW) {
      divW = newW;
      d3.select('#shelf-svg').attr('width', divW);
      resizeShelf();
    }
  }), 500);
}

// YAML laden und parsen, dann App starten
fetch('data/books.yaml')
  .then(response => response.text())
  .then(yamlText => {
    const data = jsyaml.load(yamlText);
    startApp(data);
  });