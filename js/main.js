'use strict';

//get floor/ceiling range
function getRange(arr, by) {
  return [Math.floor(_.min(arr) / by) * by, Math.ceil(_.max(arr) / by) * by];
}

//calculate when to divide books
function getDivider(datum, option) {
  let val;
  if (option === 'year_published_desc' || option === 'year_published_asc') {
    val = datum['Year Published'];
  } else {
    val = datum[option];
  }
  //get divider labels
  let label = val;
  if (option === 'year_published_desc') {
    label = -val;
  } else if (option === 'year_published_asc') {
    label = val;
  } else if (option === 'year_desc') {
    label = -val;
  } else if (option === 'first_name' || option === 'last_name') {
    label = val.charAt(0);
  } else if (option === 'serie') {
    // Gruppiere nach Serie: Buchstabe oder Serienname
    if (!val || val === 'null' || val === null) {
      label = 'No Series';
    } else {
      label = val;
    }
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
    label = Math.abs(val) < 10000 ? '<10K': (Math.floor(Math.abs(val) / 10000) * 10000 / 1000 + 'K+');
  } else if (option === 'is_not_bestseller') {
    label = !val ? 'NYT Best seller': 'Not Best Seller';
  } else if (option === 'is_english') {
    label = val ? 'English': 'Translated';
  } else if (option === 'title') {
    label = _.isNaN(+val.charAt(0)) ? val.charAt(0): '#';
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
      var r = (i & 1) == 0 ? oR: iR;
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
  d3.select('.js-modal-next').classed('is-hidden', (i < count - 1 ? false: true));
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
    bookshelves: d.bookshelves,
    Serie: d.Serie,
    pages: d.pages,
    duration: d.duration,
    bookType: d.bookType,
    My_Review: d.My_Review,
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
  
  // Set edit link with book ID parameter
  const editUrl = `book-editor.html?bookId=${d.id}`;
  d3.select('.js-edit-book-link').attr('href', editUrl);
  
  d3.select('#modal-authors').html('');
}

function getShelfWidth() {
  return Math.max(document.getElementById('shelf').clientWidth, 700)
}
//put all javascript code in eine Funktion, die nach dem Laden von books.yaml aufgerufen wird
// Hilfsfunktion für Sortierung
function getSortParams(option) {
  switch(option) {
    case 'year_published_desc': return ['Year Published', 'desc'];
    case 'year_published_asc': return ['Year Published', 'asc'];
    case 'year_desc': return ['year', 'desc'];
    case 'year_asc': return ['year', 'asc'];
    case 'rating_desc': return ['rating', 'desc'];
    case 'rating_asc': return ['rating', 'asc'];
    case 'bookshelves': return ['bookshelves', 'asc'];
    case 'serie': return ['Serie', 'asc']; // NEU: Sortierung nach Serie
    default: return [option, 'asc'];
  }
}

function startApp(data) {
  // Nur eine Sortieroption (Standard: Publikationsjahr absteigend)
  let sortOption = 'year_published_desc';
  let [sortField, sortDir] = getSortParams(sortOption);
  let books = _.orderBy(data.books, [sortField], [sortDir]);

  //add text in headline
  d3.select('#headline-count').text(books.length);
  d3.select('#headline-year-start').text(_.minBy(books, 'Year Published')?.['Year Published'] || '');
  d3.select('#headline-year-end').text(_.maxBy(books, 'Year Published')?.['Year Published'] || '');
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
      .attr('class', `js-legends${isInitial ? '': ' is-hidden'}`)
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
      .attr('class', `legend-arrow js-legends${isInitial ? '': ' is-hidden'}`)
  };

  //sort options
  let sortOptions = ['year_published_desc', 'rating_desc', 'rating_asc', 'year_published_asc'];

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
    let seriesCount = {};
    sortedBooks.forEach((d) => {
      if (d.Serie && d.Serie !== 'null') {
        seriesCount[d.Serie] = (seriesCount[d.Serie] || 0) + 1;
      }
    });
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
        // Für Serie: Spezielle Behandlung
        if (sortOption === 'serie') {
          if (d.Serie && d.Serie !== 'null' && seriesCount[d.Serie] > 2) {
            // Serien mit mehr als 2 Bänden: Serienname + Anzahl
            putLegend(`${d.Serie} (${seriesCount[d.Serie]})`, labelCount, accW, accS, isInitial, gap);
          } else {
            // Alle anderen: Verwende den normalen divider (Serie-Name oder "No Series")
            putLegend(divider, labelCount, accW, accS, isInitial, gap);
          }
        } else {
          // Alle anderen Sortieroptionen: Verwende den normalen divider
          putLegend(divider, labelCount, accW, accS, isInitial, gap);
        }
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
    return `${splitted[0]}, ${currY - (isUp ? 10: -10)})`
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
        const imageHtml = d.image_url ? `<div style="text-align: center; margin-top: 10px;"><img src="${d.image_url}" alt="${d.title}" style="max-width: 120px; max-height: 180px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"/></div>` : '';
        return `${title}<div><div class="author">by <strong>${d.author}</strong></div></div>${imageHtml}`;
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
    .append('g')
      .attr('class', (d) => {
        // Zufällige spine-Stilauswahl (ca. 20% spine-ribbed)
        const randomStyle = Math.random();
        let spineStyle = '';
        if (randomStyle < 0.2) {
          spineStyle = 'spine-ribbed';
        }
        return `book-spine genre-${d.genre || 'Unknown'} ${spineStyle}`;
      })
      .each(function(d) {
        const spine = d3.select(this);
        const width = bookW(d.pages);
        const height = bookH(d.rating);
        const spineColor = d.book_color ? d.book_color : (d.genre === 'Fiction' ? '#4a6741' : '#8B4513');
        const hasRibbedEffect = spine.classed('spine-ribbed');
        
        // Hauptbuchrücken
        spine.append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('width', width)
          .attr('height', height)
          .attr('rx', 2)
          .attr('ry', 2)
          .attr('id', `book-rect-${d.id}`)
          .attr('class', 'book-rect')
          .attr('fill', spineColor)
          .attr('stroke', '#2c1810')
          .attr('stroke-width', 0.5);
        
        // Schatten auf der rechten Seite
        spine.append('rect')
          .attr('x', width - 2)
          .attr('y', 1)
          .attr('width', 2)
          .attr('height', height - 1)
          .attr('fill', 'rgba(0,0,0,0.3)')
          .attr('rx', 1);
        
        // Lichtreflex auf der linken Seite
        spine.append('rect')
          .attr('x', 1)
          .attr('y', 1)
          .attr('width', 2)
          .attr('height', height - 2)
          .attr('fill', 'rgba(255,255,255,0.2)')
          .attr('rx', 1);
        
        // Ribbed-Effekt (horizontale Linien)
        if (hasRibbedEffect && height > 20) {
          const numberOfRibs = Math.floor(height / 15);
          const ribSpacing = height / (numberOfRibs + 1);
          
          for (let i = 1; i <= numberOfRibs; i++) {
            const ribY = ribSpacing * i;
            
            // Schatten-Linie (dunkler)
            spine.append('line')
              .attr('x1', 2)
              .attr('y1', ribY)
              .attr('x2', width - 2)
              .attr('y2', ribY)
              .attr('stroke', 'rgba(0,0,0,0.3)')
              .attr('stroke-width', 1)
              .attr('class', 'spine-separator');
            
            // Highlight-Linie (heller)
            spine.append('line')
              .attr('x1', 2)
              .attr('y1', ribY + 1)
              .attr('x2', width - 2)
              .attr('y2', ribY + 1)
              .attr('stroke', 'rgba(255,255,255,0.2)')
              .attr('stroke-width', 1)
              .attr('class', 'spine-separator-highlight');
          }
        }
        
        // Normale Textur-Linien für nicht-ribbed Bücher
        if (!hasRibbedEffect && width > 8) {
          // Vertikale Texturlinien für Buchrücken-Effekt
          for (let i = 3; i < width - 3; i += 3) {
            spine.append('line')
              .attr('x1', i)
              .attr('y1', 2)
              .attr('x2', i)
              .attr('y2', height - 2)
              .attr('stroke', 'rgba(255,255,255,0.1)')
              .attr('stroke-width', 0.5);
          }
        }
        
        // Horizontale Dekorationslinien (nur für nicht-ribbed Bücher)
        if (!hasRibbedEffect && height > 30) {
          spine.append('rect')
            .attr('x', 2)
            .attr('y', 8)
            .attr('width', width - 4)
            .attr('height', 1)
            .attr('fill', 'rgba(255,255,255,0.15)');
            
          spine.append('rect')
            .attr('x', 2)
            .attr('y', height - 10)
            .attr('width', width - 4)
            .attr('height', 1)
            .attr('fill', 'rgba(255,255,255,0.15)');
        }
      });
  //draw age overlay (optional, falls Feld vorhanden)
  // Bestseller und Sprache korrekt behandeln
  _.each(_.filter(books, (d) => d.bestseller), (d) => {
    // Füge Bestseller-Stern direkt in die book-spine group hinzu
    d3.select(`#book-${d.id} .book-spine`)
      .append('text')
      .attr('x', bookW(d.pages) / 2) // Mittig horizontal
      .attr('y', 20) // 20px Abstand zur oberen Kante
      .attr('text-anchor', 'middle')
      .attr('fill', '#FFD700')
      .attr('font-size', '8')
      .attr('stroke', '#B8860B')
      .attr('stroke-width', '0.3')
      .style('text-shadow', '1px 1px 1px rgba(0,0,0,0.7)')
      .text('★');
  });
  
  // Audiobook Symbol für Bücher mit bookType="Audiobook"
  _.each(_.filter(books, (d) => d.bookType === 'Audiobook'), (d) => {
    const spine = d3.select(`#book-${d.id} .book-spine`);
    const width = bookW(d.pages);
    const height = bookH(d.rating);
    const iconSize = 16; // Doppelt so groß (war 8)
    const iconX = (width - iconSize) / 2; // Mittig horizontal
    const iconY = height - 25 - iconSize; // 25px Abstand zur unteren Kante
    
    // Erstelle SVG-Gruppe für das Lautsprecher-Icon
    const iconGroup = spine.append('g')
      .attr('transform', `translate(${iconX}, ${iconY})`);
    
    // Schatten-Element (leicht versetzt nach unten rechts)
    iconGroup.append('g')
      .attr('transform', 'translate(1, 1)')
      .attr('opacity', '0.3')
      .append('path')
      .attr('d', `M 2 4 L 6 4 L 10 2 L 10 14 L 6 12 L 2 12 Z`)
      .attr('fill', 'black')
      .attr('stroke', 'none');
    
    // Schatten für Schallwellen
    const shadowGroup = iconGroup.append('g')
      .attr('transform', 'translate(1, 1)')
      .attr('opacity', '0.3');
      
    shadowGroup.append('path')
      .attr('d', 'M 12 6 Q 14 8 12 10')
      .attr('fill', 'none')
      .attr('stroke', 'black')
      .attr('stroke-width', '1')
      .attr('stroke-linecap', 'round');
      
    shadowGroup.append('path')
      .attr('d', 'M 13 4 Q 16 8 13 12')
      .attr('fill', 'none')
      .attr('stroke', 'black')
      .attr('stroke-width', '0.8')
      .attr('stroke-linecap', 'round');
      
    shadowGroup.append('path')
      .attr('d', 'M 14 2 Q 18 8 14 14')
      .attr('fill', 'none')
      .attr('stroke', 'black')
      .attr('stroke-width', '0.6')
      .attr('stroke-linecap', 'round');
    
    // Hauptsymbol (komplett weiß)
    iconGroup.append('path')
      .attr('d', `M 2 4 L 6 4 L 10 2 L 10 14 L 6 12 L 2 12 Z`)
      .attr('fill', 'white')
      .attr('stroke', 'white')
      .attr('stroke-width', '0.5');
    
    // Schallwellen (komplett weiß)
    iconGroup.append('path')
      .attr('d', 'M 12 6 Q 14 8 12 10')
      .attr('fill', 'none')
      .attr('stroke', 'white')
      .attr('stroke-width', '1')
      .attr('stroke-linecap', 'round');
      
    iconGroup.append('path')
      .attr('d', 'M 13 4 Q 16 8 13 12')
      .attr('fill', 'none')
      .attr('stroke', 'white')
      .attr('stroke-width', '0.8')
      .attr('stroke-linecap', 'round');
      
    iconGroup.append('path')
      .attr('d', 'M 14 2 Q 18 8 14 14')
      .attr('fill', 'none')
      .attr('stroke', 'white')
      .attr('stroke-width', '0.6')
      .attr('stroke-linecap', 'round');
  });
  
  // Markiere NUR Bücher im Bookshelf 'to-read' mit schwarzem Winkel
  _.each(_.filter(books, (d) => typeof d.bookshelves === 'string' && d.bookshelves.trim().toLowerCase() === 'to-read'), (d) => {
    d3.select(`#book-${d.id} .book-spine`)
      .append('path')
      .attr('d', `M 0 0 h ${bookWRange[0]} l -${bookWRange[0]} ${bookWRange[0]} z`)
      .attr('class', 'translated')
      .attr('fill', '#3B3A38');
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
        const title = (d.title || '').toLowerCase();
        const author = (d.author || '').toLowerCase();
        const publisher = (d.publisher || '').toLowerCase();
        return title.indexOf(entered) > -1 ||
          author.indexOf(entered) > -1 ||
          publisher.indexOf(entered) > -1;
      });
      //show only books exists by the typed letters
      if (filtered.length > 0) {
        const bookIds = filtered.map((d) => d.id);
        const searched = filtered.map((d, i) => {
          let titleFormatted = d.title || '';
          const splitted = titleFormatted.split(':')
          if (splitted.length > 1) {
            titleFormatted = `${splitted[0].toUpperCase()}:${splitted[1]}`;
          }
          let title = getSearchedText(titleFormatted, entered);
          let name = getSearchedText(d.author || '', entered);
          let publisher = getSearchedText(d.publisher || '', entered);
          return `<li class="item js-search-list js-search-${i}" search-id="${i}" id="search-${i}">${title}<br/>by ${name}, ${publisher}</li>`
        });
        //add list to <ul>
        d3.selectAll('.js-search-elm').classed('is-hidden', false);
        d3.select('#search-result')
          .html(`<li class="count" id="search-count"><i>${searched.length}</i> book${searched.length > 1 ? 's': ''} found</a></li>${searched.join(' ')}`);
        //height of the count line
        const countH = document.getElementById('search-count').clientHeight;
        //down arrow pressed
        if (d.keyCode === 40) {
          selectedId = selectedId < searched.length - 1 ? selectedId + 1: 0;
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
          selectedId = selectedId > 0 ? selectedId - 1: searched.length - 1;
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
fetch('data/Meine_Buchliste.yaml')
  .then(response => response.text())
  .then(yamlText => {
    const data = (typeof jsyaml !== 'undefined' ? jsyaml : YAML).load(yamlText);
    console.log('Loaded YAML data:', data);
    console.log('First book Serie field:', data.books[0].Serie);
    startApp(data);
  });