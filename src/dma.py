from math import *
from pathlib import Path
from PIL import Image
from utility import *


# Function to compute distance and projection transforms of binary image pixels
def integer_transforms(pixels, visualise_as_image=False):
    # Get shape of image
    n = len(pixels)
    m = len(pixels[0])

    # Initialise 1D distance transform g and 1D projection transform P1d to infinity for all points
    g = [[INF for j in range(m)] for i in range(n)]
    P1d = [[(INF, INF) for j in range(m)] for i in range(n)]

    # For each x coordinate
    for x in range(n):
        # For y = 0, if white point, distance is 0 and projection is the point itself
        if pixels[x][0] == WHITE:
            g[x][0] = 0
            P1d[x][0] = (x, 0)

        # For each y coordinate after y = 0
        for y in range(1, m):
            # If white point, distance is 0 and projection is the point itself
            if pixels[x][y] == WHITE:
                g[x][y] = 0
                P1d[x][y] = (x, y)
            # Else, update the 1D transforms appropriately
            else:
                g[x][y] = g[x][y - 1] + 1
                if g[x][y] > INF:
                    g[x][y] = INF
                P1d[x][y] = P1d[x][y - 1]

        # For each y coordinate in reverse order after y = m - 1
        for y in range(m - 2, -1, -1):
            # Correct the 1D transform
            if g[x][y + 1] < g[x][y]:
                g[x][y] = g[x][y + 1] + 1
                if g[x][y] > INF:
                    g[x][y] = INF
                P1d[x][y] = P1d[x][y + 1]

    # Initialise 2D distance square transform D2 and 2D projection transform P
    D2 = [[INF for j in range(m)] for i in range(n)]
    P = [[(INF, INF) for j in range(m)] for i in range(n)]

    # For each y coordinate
    for y in range(m):
        # Apply the Hirata-Hessellink Algorithm to get square distance and projection transforms for each point
        s = [INF for i in range(n + 1)]
        t = [INF for i in range(n + 1)]
        q = 0
        s[q] = 0
        t[q] = 0
        for x in range(1, n):
            while s[q] > 0 and (t[q] - s[q]) ** 2 + g[s[q] - 1][y] ** 2 > (t[q] - (x + 1)) ** 2 + g[x][y] ** 2:
                q -= 1
            sep = ((x + 1) ** 2 - s[q] ** 2 + g[x][y] ** 2 - g[s[q] - 1][y] ** 2) // (2 * ((x + 1) - s[q]))
            if q < 0:
                q = 0
                s[q] = x + 1
            elif 1 + sep <= n:
                q += 1
                s[q] = x + 1
                t[q] = 1 + sep
        for x in range(n - 1, -1, -1):
            D2[x][y] = ((x + 1) - s[q]) ** 2 + g[s[q] - 1][y] ** 2
            P[x][y] = P1d[s[q] - 1][y]
            if (x + 1) == t[q]:
                q -= 1

    if visualise_as_image:
        # Save the visualisation of the distance squared transform
        visualise(D2, Path(__file__).parent.parent / "images/distance_transform.png")

    # Return the 2D transforms
    return D2, P


# Function to save the visualisation of distance transforms as an image
def visualise(transform, path):
    n = len(transform)
    m = len(transform[0])
    im = Image.new(mode="L", size=(m, n))
    data = []
    max_dist = 0
    for i in transform:
        for j in i:
            max_dist = max(max_dist, j)
    # Scale the distance transform values from 0 to 255 (255 is white/far, 0 is black/close)
    normaliser = 255 / max_dist ** 0.5
    for i in range(n):
        for j in range(m):
            data.append(255 - transform[i][j] ** 0.5 * normaliser)
    im.putdata(data)
    im.save(path)


# Function to get the (approximate) real valued distance squared transform
def real_transform(z, D2, fast=False):
    # If FDMA used instead of just DMA
    if fast:
        # Approximate the real point to an integer point
        z = (round(z[0]), round(z[1]))
        # If in bounds return the D2 value, otherwise return infinity
        try:
            return D2[z[0]][z[1]]
        except IndexError:
            return INF
    # If DMA is used, not FDMA
    # Calculate minimum D2 value of all 4 integer neighbour points of z
    d2 = INF
    N = ((floor(z[0]), floor(z[1])), (floor(z[0]), ceil(z[1])), (ceil(z[0]), floor(z[1])), (ceil(z[0]), ceil(z[1])))
    for p in N:
        try:
            d2 = min(d2, D2[p[0]][p[1]])
        except IndexError:
            pass
    # Return minimum D2 value
    return d2


# Function to return distance between two points
def dist(u, v):
    return sqrt((u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2)


# Function to test a particular line segment for having a delta value higher than the threshold
def test_segment(p1, p2, delta, D2, fast=False):
    # Calculate distance l
    l = dist(p1, p2)
    # If l is less than double the threshold, delta can never be more than threshold
    if l < 2 * delta:
        return False
    # Start searching from midpoint in both directions
    a_plus = 0.5
    a_minus = 0.5
    z_minus = (a_minus * p1[0] + (1 - a_minus) * p2[0], a_minus * p1[1] + (1 - a_minus) * p2[1])
    z_plus = (a_plus * p1[0] + (1 - a_plus) * p2[0], a_plus * p1[1] + (1 - a_plus) * p2[1])
    d_minus = real_transform(z_minus, D2)
    d_plus = real_transform(z_plus, D2)
    # If a d value crosses threshold then so does delta
    if d_minus > delta or d_plus > delta:
        return True
    # Update the search points on the line segment
    a_minus = a_minus - (delta - d_minus) / l
    a_plus = a_plus + (delta - d_plus) / l
    # Repeat until points become too close to the endpoints (in that case, delta cannot be higher than threshold)
    while dist(z_minus, p1) >= delta or dist(z_plus, p2) >= delta:
        # To handle edge cases
        if a_minus < 0 and a_plus > 1:
            break
        if a_minus >= 0:
            z_minus = (a_minus * p1[0] + (1 - a_minus) * p2[0], a_minus * p1[1] + (1 - a_minus) * p2[1])
            d_minus = real_transform(z_minus, D2, fast)
            # If a d value crosses threshold then so does delta
            if d_minus >= delta:
                return True
            # Update the search points on the line segment
            a_minus = a_minus - (delta - d_minus) / l
        if a_plus <= 1:
            z_plus = (a_plus * p1[0] + (1 - a_plus) * p2[0], a_plus * p1[1] + (1 - a_plus) * p2[1])
            d_plus = real_transform(z_plus, D2, fast)
            # If a d value crosses threshold then so does delta
            if d_plus >= delta:
                return True
            # Update the search points on the line segment
            a_plus = a_plus + (delta - d_plus) / l
    # If delta never crossed threshold, it will not
    return False


# Function to compute the Delta Medial Axis of a binary image
def compute_dma(pixels, delta, fast=False, D2=None, P=None):
    # Get the shape of matrix
    n = len(pixels)
    m = len(pixels[0])
    # Compute D2 and P if not provided
    if D2 is None or P is None:
        D2, P = integer_transforms(pixels)
    # Initialise the DMA to be empty
    dma = [[False for j in range(m)] for i in range(n)]
    # For every pixel
    for x in range(1, n):
        for y in range(1, m):
            u = (x, y)
            # Ignore if point is white
            if pixels[u[0]][u[1]] == WHITE:
                continue
            # Check the two backward neighbour points to generate the line segments
            # (forward neighbours will be checked by next points)
            for v in ((x - 1, y), (x, y - 1)):
                # Ignore if neighbour is white
                if pixels[v[0]][v[1]] == WHITE:
                    continue
                # Fetch the projection transforms of u and v
                p1 = P[u[0]][u[1]]
                p2 = P[v[0]][v[1]]
                # Test the segment to see if its delta is significant (more than threshold)
                if test_segment(p1, p2, delta, D2, fast):
                    mid = ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
                    # Additional checks to get a thinner skeleton
                    if dist(mid, p1) >= dist(mid, p2):
                        dma[u[0]][u[1]] = True
                    if dist(mid, p1) <= dist(mid, p2):
                        dma[v[0]][v[1]] = True
    # Return the computed DMA
    return dma


# Function to format the DMA data
def format_dma(dma, D2, skip=3):
    # Get the shape
    n = len(dma)
    m = len(dma[0])

    # Create three lists (corresponding to tuples (x, y, D2))
    x_list = []
    y_list = []
    D2_list = []
    # Run a DFS on the graph formed by the DMA
    visited = [[False for j in range(m)] for i in range(n)]
    stack = []
    for i in range(n):
        for j in range(m):
            if visited[i][j] or not dma[i][j]:
                continue
            visited[i][j] = True
            stack.append((i, j, 0))
            while stack:
                # cycle_index varies from 0 to skip - 1
                # Point is accepted only if cycle_index is 0
                # Effectively skipping all but 1 out of every skip points
                x, y, cycle_index = stack.pop()
                if cycle_index == 0:
                    x_list.append(x)
                    y_list.append(y)
                    D2_list.append(D2[x][y])
                else:
                    # Also update the skipped point, otherwise points might be reconsidered
                    dma[x][y] = False
                # Check all neighbours
                for xx, yy in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1),
                               (x + 1, y + 1), (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1)):
                    try:
                        if visited[xx][yy] or not dma[xx][yy]:
                            continue
                        visited[xx][yy] = True
                        # Increase cycle_index by 1 for neighbour points
                        stack.append((xx, yy, (cycle_index + 1) % skip))
                    except IndexError:
                        pass
    return x_list, y_list, D2_list


# Function to compress the DMA data into a binary .axy file
def write_to_file(n, m, x_list, y_list, D2_list, path):
    with open(path, 'ab') as f:
        # Get number of points
        l = len(x_list)
        # Compress x, y, z into a single integer t
        t = [D2_list[i] * n * m + x_list[i] * m + y_list[i] for i in range(l)]
        # Use the limit to make a fixed-length encoding
        limit = n * m * (n * n + m * m) + n * m + m
        bits = (limit.bit_length() + 7) // 8

        # Encode numbers into bytes (little-endian)
        byte_array = bytearray()
        for val in t:
            byte_array.extend(val.to_bytes(bits, 'little'))
        # Write the entire byte array to file
        f.write(byte_array)
