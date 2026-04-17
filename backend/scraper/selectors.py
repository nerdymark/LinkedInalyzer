# LinkedIn feed extraction via JavaScript.
# LinkedIn uses obfuscated class names, so we use structural/attribute-based
# selectors and JS evaluation instead of CSS selectors.

# The main feed container
FEED_CONTAINER = '[data-component-type="LazyColumn"]'

# Feed items have this attribute
FEED_ITEM_ATTR = 'data-display-contents'

# JavaScript to extract all visible posts from the feed.
# Returns a list of {content, author_name, author_url, author_headline, post_id}
EXTRACT_POSTS_JS = """() => {
    // Find the largest LazyColumn (the main feed)
    const cols = document.querySelectorAll('[data-component-type="LazyColumn"]');
    let mainCol = null;
    let maxChildren = 0;
    for (const col of cols) {
        if (col.children.length > maxChildren) {
            maxChildren = col.children.length;
            mainCol = col;
        }
    }
    if (!mainCol) return [];

    const posts = [];
    for (const child of mainCol.children) {
        // Feed posts have data-display-contents="true" and text starting with "Feed post"
        if (child.getAttribute('data-display-contents') !== 'true') continue;
        const fullText = child.innerText || '';
        if (!fullText.startsWith('Feed post')) continue;
        if (fullText.length < 50) continue;  // skip tiny items (ads, pills)

        // Extract feed context — the line between "Feed post" and the author name
        // e.g. "Based on your profile and activity", "X likes this", "X commented"
        let feedContext = '';
        const lines = fullText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // lines[0] is "Feed post", lines[1+] may be context before the author
        for (let i = 1; i < Math.min(lines.length, 5); i++) {
            const line = lines[i];
            if (line.includes('likes this') || line.includes('commented') ||
                line.includes('loves this') || line.includes('celebrates this') ||
                line.includes('finds this insightful') || line.includes('finds this funny') ||
                line.includes('supports this') || line.includes('reposted this') ||
                line.includes('follow this') || line.includes('follows this') ||
                line.includes('Based on your') || line.includes('Suggested') ||
                line.includes('Promoted') || line.includes('connections follow')) {
                feedContext = line;
                break;
            }
        }
        // If no specific context found, it's likely a direct connection's post
        if (!feedContext) feedContext = 'direct';

        // Extract author from first profile link with text
        const profileLinks = child.querySelectorAll('a[href*="/in/"]');
        let authorName = '';
        let authorUrl = '';
        for (const pl of profileLinks) {
            let text = pl.innerText?.trim().split('\\n')[0]?.trim() || '';
            // Strip LinkedIn UI chrome from author names
            text = text.replace(/\\s*(Verified Profile|Premium Profile|\\d+(st|nd|rd|th)\\+?|Open to work|Hiring)\\s*/gi, ' ').trim();
            if (text.length > 1) {
                authorName = text;
                authorUrl = pl.href.split('?')[0];
                break;
            }
        }

        // If no /in/ profile link, look for company pages
        if (!authorUrl) {
            const companyLinks = child.querySelectorAll('a[href*="/company/"]');
            for (const cl of companyLinks) {
                const text = cl.innerText?.trim().split('\\n')[0]?.trim() || '';
                if (text.length > 1) {
                    authorName = text;
                    authorUrl = cl.href.split('?')[0];
                    break;
                }
            }
        }

        if (!authorName) continue;  // skip if we can't identify who posted

        // Extract post content - find the longest text block
        // Skip the "Feed post" prefix and context lines
        const spans = child.querySelectorAll('span');
        let longestText = '';
        for (const span of spans) {
            const t = span.innerText?.trim() || '';
            // Must be substantial and not be just UI chrome
            if (t.length > longestText.length && t.length > 30 && span.children.length < 5) {
                // Exclude common UI patterns
                if (!t.startsWith('Feed post') && !t.startsWith('Reaction button') &&
                    !t.startsWith('Beginning of dialog') && !t.startsWith('Sort by:')) {
                    longestText = t;
                }
            }
        }

        if (!longestText || longestText.length < 20) continue;  // skip posts with no real content

        // Try to find author headline (usually the line after the name in the post header)
        let headline = '';
        const allText = fullText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: after author name, there's usually a connection degree, then headline
        for (let i = 0; i < allText.length && i < 10; i++) {
            const line = allText[i];
            if (line.includes(' at ') || line.includes('CEO') || line.includes('Engineer') ||
                line.includes('Director') || line.includes('Manager') || line.includes('VP') ||
                line.includes('Founder') || line.includes('followers')) {
                headline = line;
                break;
            }
        }

        // Generate a pseudo-ID from author + content hash (avoid btoa for unicode safety)
        const raw = authorUrl + '|' + longestText.substring(0, 100);
        let hash = 0;
        for (let i = 0; i < raw.length; i++) {
            hash = ((hash << 5) - hash + raw.charCodeAt(i)) | 0;
        }
        const postId = 'post_' + Math.abs(hash).toString(36);

        posts.push({
            content: longestText,
            author_name: authorName,
            author_url: authorUrl,
            author_headline: headline,
            post_id: postId,
            feed_context: feedContext,
        });
    }
    return posts;
}"""

# JavaScript to click "see more" / expand truncated posts
EXPAND_POSTS_JS = """() => {
    // Look for buttons/links that expand truncated text
    const expandButtons = document.querySelectorAll('button, a');
    let clicked = 0;
    for (const btn of expandButtons) {
        const text = btn.innerText?.trim().toLowerCase() || '';
        if (text === '…see more' || text === 'see more' || text === '...see more') {
            btn.click();
            clicked++;
        }
    }
    return clicked;
}"""
