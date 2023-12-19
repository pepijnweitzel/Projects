import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Get set of links page forwards to
    links = corpus[page]

    # List of all pages in corpus
    all_pages = [key for key in corpus.keys()]

    # Create dictionary for probability distribution
    probability_distribution = {}
    for page in all_pages:
        probability_distribution[page] = 0.0

    # If page has no links, equal chance to go to any page in corpus
    if len(links) == 0:
        p = 1.0 / len(all_pages)
        for page in all_pages:
            probability_distribution[page] = p
            return probability_distribution

    # If page does have links, calculate chance to go to every page
    else:
        # Chance of 1 - damping factor to go to any random page in corpus
        x = 1.0 - damping_factor
        x = x / len(all_pages)
        for page in all_pages:
            probability_distribution[page] = x
        # Chance of damping factor to follow any random link in page
        y = damping_factor / len(links)
        for page in links:
            probability_distribution[page] += y

    return probability_distribution

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # List of all pages in corpus
    all_pages = [key for key in corpus.keys()]

    # Get first sample
    page = []
    first_page = random.choice(all_pages)
    page.append(first_page)
    n -= 1

    # Store number of page visits of each page in a dict
    page_visits = {}
    for html in all_pages:
        page_visits[html] = 0

    # Repeat n times for n samples
    for _ in range(n):
        # Add 1 to the value page_visits of current page
        page_visits[page[0]] += 1
        # Get probability distribution of current page for next page and create tuple for weighted random choiche
        pb = transition_model(corpus, page[0], damping_factor)
        weights = (pb[key]*10 for key in all_pages)
        # Choose random page based on weighted random choiche
        page = random.choices(all_pages, weights=weights)

    # Change page_visits' values into proper ranking values
    for key in page_visits:
        page_visits[key] = page_visits[key] / n

    return page_visits

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # List of all pages in corpus
    all_pages = [key for key in corpus.keys()]

    # Create PageRank dictionary
    page_rank = {}
    for page in all_pages:
        page_rank[page] = 1 / len(all_pages)

    run = True
    while run:
        old_page_ranks = copy.copy(page_rank)
        new_page_rank = copy.copy(page_rank)
        changes = []

        for page in all_pages:
            # Store old PageRank
            old_page_rank = old_page_ranks[page]
            # Initialize the new PageRank value to (1 - damping factor) / (number of all pages)
            new_page_rank[page] = (1 - damping_factor) / len(all_pages)
            # Make dict to store all links that link to current page, and their number of links on their page
            parent_pages = {}
            for key in corpus.keys():
                if page in corpus[key]:
                    parent_pages[key] = len(corpus[key])
            # Perform the iterative function
            for key in parent_pages.keys():
                new_page_rank[page] += damping_factor * old_page_ranks[key] / parent_pages[key]

            # Add change to changes list to later check
            change = old_page_rank - new_page_rank[page]
            if abs(change) > 0.001:
                changes.append(change)

        # Update all page ranks
        page_rank = new_page_rank

        # Check whether the value of changes made are correct by norm
        if len(changes) == 0:
            run = False

    return page_rank


if __name__ == "__main__":
    main()
